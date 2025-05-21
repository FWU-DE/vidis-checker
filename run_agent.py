import argparse
import asyncio
import base64
import json
import os
import random
import string
import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from src.files.zip import create_zip_archive
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent, Controller, ActionResult  # type: ignore
from browser_use.browser.browser import (  # type: ignore
    Browser,
    BrowserConfig,
    BrowserContextConfig,
)
from browser_use.browser.context import (  # type: ignore
    BrowserContextWindowSize,
    BrowserContext,
)
from playwright.sync_api import Request  # type: ignore

from src.agent.tasks import get_task
from src.models.models import (
    Cookie,
    LocalStorage,
    NetworkRequest,
    NetworkRequestResponsePair,
    NetworkResponse,
    Resource,
    SessionStorage,
    StepResult,
)

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Global variables
WINDOW_SIZE = BrowserContextWindowSize(width=1280, height=1100)
OUTPUT_DIR = "./agent_results"
GIF_DURATION = 3500.0


class VidisAgent:
    def __init__(
        self,
        task: Dict[str, Any],
        output_name: str,
        headless: bool = False,
        disable_security: bool = True,
        minimum_wait_page_load_time: int = 2,
        maximum_wait_page_load_time: int = 15,
    ):
        self.browser = Browser(
            config=BrowserConfig(
                headless=headless,
                disable_security=disable_security,
                new_context_config=BrowserContextConfig(
                    disable_security=disable_security,
                    minimum_wait_page_load_time=minimum_wait_page_load_time,
                    maximum_wait_page_load_time=maximum_wait_page_load_time,
                    browser_window_size=WINDOW_SIZE,
                ),
            )
        )
        self.controller = Controller()
        self.llm = ChatOpenAI(model="gpt-4o")

        self.register_actions()
        self.request_response_pairs: List[NetworkRequestResponsePair] = []
        self.request_listener: Optional[Callable] = None
        self.task = task
        self.output_name = output_name

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, output_name), exist_ok=True)

    def register_actions(self):
        """Register custom actions with the controller."""

        @self.controller.action(
            "Save the page of type: page_type (privacy_policy, imprint, terms_of_use, register, logout) as pdf in the current task folder"
        )
        async def save_page_as_pdf(page_type: str) -> ActionResult:
            try:
                page = self.browser.playwright_browser.contexts[0].pages[0]
                output_dir = os.path.join(OUTPUT_DIR, self.output_name)
                os.makedirs(output_dir, exist_ok=True)

                pdf_filename = f"{page_type}.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)

                await page.pdf(path=str(pdf_path))

                return ActionResult(
                    extracted_content=f"{page_type} Page saved as PDF: {pdf_path}"
                )
            except Exception as e:
                return ActionResult(error=f"Failed to save page as PDF: {str(e)}")

        @self.controller.action("Scroll to bottom of the page")
        async def scroll_to_bottom() -> ActionResult:
            try:
                page = self.browser.playwright_browser.contexts[0].pages[0]
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                return ActionResult(extracted_content="Scrolled to bottom of the page.")
            except Exception as e:
                return ActionResult(error=f"Failed to scroll: {str(e)}")

        @self.controller.action("cookie_handler: save the cookies as screenshots")
        async def cookie_handler() -> ActionResult:
            try:
                page = self.browser.playwright_browser.contexts[0].pages[0]

                # TODO: Check URL
                page_url = page.url

                output_dir = os.path.join(OUTPUT_DIR, self.output_name)
                screenshot_path = os.path.join(output_dir, "cookie_banner.jpg")

                screenshot_bytes = await page.screenshot()
                image = Image.open(BytesIO(screenshot_bytes))
                image.save(screenshot_path, "JPEG", quality=85)

                data = {
                    "url": page_url,
                    "timestamp": int(time.time()),
                    "screenshot_filename": "cookie_banner.jpg",
                    "screenshot_path": str(screenshot_path),
                }

                with open(
                    os.path.join(output_dir, "cookie_banner.jsonl"), "a", encoding="utf-8"
                ) as f:
                    f.write(json.dumps(data) + "\n")

                return ActionResult(extracted_content="Cookies saved successfully.")
            except Exception as e:
                return ActionResult(error=f"Failed to save cookies: {str(e)}")

    def setup_network_tracking(self, context: BrowserContext):
        """Set up network request tracking for the browser context."""

        async def on_response(response) -> None:
            print(response)

            request = response.request

            request_data = NetworkRequest(
                url=request.url,
                method=request.method,
                headers=request.headers,
                resource_type=request.resource_type,
                task_name=self.task["name"],
                timestamp=time.time(),
                post_data=request.post_data,
            )

            response_text = None
            try:
                response_text = await response.text()
            except Exception as e:
                print(f"Failed to get response text: {e}")

            response_data = NetworkResponse(
                url=response.url,
                headers=response.headers,
                status=response.status,
                text=response_text,
            )
            
            request_response_pair = NetworkRequestResponsePair(
                request=request_data,
                response=response_data,
            )
            self.request_response_pairs.append(request_response_pair)

        context.on("response", on_response)
        return on_response

    async def get_step_result(self, agent_obj) -> ActionResult:
        """Collect current browser data including cookies, local storage, and session storage."""
        try:
            # Get browser context and current page
            context = self.browser.playwright_browser.contexts[0]

            # Set up network tracking on first call
            if not hasattr(self, "request_listener") or self.request_listener is None:
                print("First step: setting up network tracking...")
                self.request_listener = self.setup_network_tracking(context)

            page = context.pages[0]
            url = page.url

            cookies = await context.cookies()

            local_storage = await page.evaluate(
                """() => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            }"""
            )

            session_storage = await page.evaluate(
                """() => {
                const items = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
            }"""
            )

            resources_raw = await page.evaluate(
                """() => {
                const resources = [];
                const elements = document.querySelectorAll('img, iframe, script, object, embed');
                elements.forEach(el => {
                    let src = el.src || el.data;
                    if (src) {
                        resources.push({
                            type: el.tagName.toLowerCase(),
                            url: src,
                            width: el.width || null,
                            height: el.height || null,
                            id: el.id || null,
                            className: el.className || null
                        });
                    }
                });
                return resources;
            }"""
            )

            resources = [Resource.model_validate(item) for item in resources_raw]

            print("🚨🚨🚨 !!!Browser data!!! 🚨🚨🚨")
            # Create a StepResult object using the Pydantic model
            step_result = StepResult(
                url=url,
                cookies=[Cookie.model_validate(cookie) for cookie in cookies],
                local_storage=LocalStorage(entries=local_storage),
                session_storage=SessionStorage(entries=session_storage),
                resources=resources,
                request_response_pairs=self.request_response_pairs
            )

            # Clear network request response pairs after each step
            self.request_response_pairs = []

            output_dir = os.path.join(OUTPUT_DIR, self.output_name)
            with open(
                os.path.join(output_dir, "step_result.jsonl"), "a", encoding="utf-8"
            ) as f:
                f.write(json.dumps(step_result.model_dump()) + "\n")

            return ActionResult(extracted_content=step_result.model_dump())
        except Exception as e:
            return ActionResult(error=f"Failed to retrieve browser data: {str(e)}")

    def create_gif_from_history(self, history_data: List[Dict], output_name: str):
        """Create an animated GIF from the agent's history with text in a dedicated bottom area."""
        frames = []
        output_dir = os.path.join(OUTPUT_DIR, output_name)
        gif_path = os.path.join(output_dir, f"history_animation_{output_name}.gif")

        # Define text area height
        text_area_height = 150  # Adjust based on your needs
        font_size = 20
        font = ImageFont.load_default(size=font_size)
        margin = 10

        for entry in history_data:
            # Get the base64 screenshot
            screenshot_base64 = entry.get("state", {}).get("screenshot", "")
            if not screenshot_base64:
                continue

            # Decode the screenshot
            try:
                image_data = base64.b64decode(screenshot_base64)
                screenshot = Image.open(BytesIO(image_data)).convert("RGB")

                # Create a new image with additional space at the bottom for text
                width, height = screenshot.size
                new_image = Image.new(
                    "RGB", (width, height + text_area_height), (255, 255, 255)
                )

                # Paste the screenshot at the top
                new_image.paste(screenshot, (0, 0))

                # Draw a separator line
                draw = ImageDraw.Draw(new_image)
                draw.line([(0, height), (width, height)], fill=(200, 200, 200), width=2)

                # Get overlay text
                text_lines = []
                model_output = entry.get("model_output", {})
                if "current_state" in model_output:
                    text_lines.append(
                        "Goal: " + model_output["current_state"].get("next_goal", "")
                    )

                for result in entry.get("result", []):
                    extracted_content = result.get("extracted_content", "")
                    # Truncate long text
                    if len(str(extracted_content)) > 100:
                        extracted_content = str(extracted_content)[:97] + "..."
                    text_lines.append(extracted_content)

                # Draw the text in the dedicated area
                y = height + margin
                for line in text_lines:
                    # Handle text wrapping for long lines
                    words = str(line).split()
                    line_text = ""
                    for word in words:
                        test_text = f"{line_text} {word}".strip()
                        bbox = font.getbbox(test_text)
                        if bbox[2] < width - (margin * 2):
                            line_text = test_text
                        else:
                            draw.text((margin, y), line_text, font=font, fill=(0, 0, 0))
                            # Ensure text_height is an integer
                            text_height = int(
                                font.getbbox(line_text)[3] - font.getbbox(line_text)[1]
                            )
                            y += text_height + 5
                            line_text = word

                    if line_text:
                        draw.text((margin, y), line_text, font=font, fill=(0, 0, 0))
                        # Ensure text_height is an integer
                        text_height = int(
                            font.getbbox(line_text)[3] - font.getbbox(line_text)[1]
                        )
                        y += text_height + 5

                # Convert PIL Image to numpy array for imageio
                numpy_frame = np.array(new_image)
                frames.append(numpy_frame)

            except Exception as e:
                print(f"Failed to process screenshot: {e}")
                continue

        # Save as GIF
        if frames:
            try:
                with open(str(gif_path), "wb") as f:
                    imageio.mimwrite(f, frames, format="GIF", duration=GIF_DURATION)
                print(f"GIF saved to {gif_path}")
            except Exception as e:
                print(f"Failed to save GIF: {e}")
        else:
            print("No frames were created.")

    async def run_task(self, max_steps: int = 25):
        """Run the task."""
        output_dir = os.path.join(OUTPUT_DIR, self.output_name)
        os.makedirs(output_dir, exist_ok=True)

        initial_actions = [{"go_to_url": {"url": self.task["url"]}}]

        agent = Agent(
            task=self.task["task"],
            llm=self.llm,
            browser=self.browser,
            validate_output=True,
            controller=self.controller,
            initial_actions=initial_actions,
            enable_memory=True,
        )

        history = await agent.run(
            on_step_end=self.get_step_result,
            max_steps=max_steps,
        )

        history_path = os.path.join(output_dir, "history.json")
        history.save_to_file(str(history_path))

        with open(history_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            self.create_gif_from_history(history_data["history"], self.output_name)

        self.create_zip_archive(self.output_name)

    def create_zip_archive(self, output_name: str):
        """Create a zip file of the task directory."""
        output_dir = os.path.join(OUTPUT_DIR, output_name)
        
        # Generate zip filename based on output name
        zip_filename = f"{output_name}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)
        
        create_zip_archive(str(output_dir), str(zip_path))
        print(f"Created zip archive at: {zip_path}")


async def main():
    parser = argparse.ArgumentParser(description="Crawl the web and save the data")
    parser.add_argument(
        "--task",
        type=str,
        default="login",
        help="Run a specific task by name. Options are login, legal, student, teacher, register, logout",
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the website to crawl",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Name of the output directory and zip file (without extension)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=25,
        help="Maximum number of steps to run",
    )
    args = parser.parse_args()
    task = get_task(args.url, args.task)
    if not task:
        print(f"Task '{args.task}' not found")
        return
    
    output_name = args.output or f"task_{args.task}_{args.url}"
    automation = VidisAgent(task=task, output_name=output_name)
    await automation.run_task(max_steps=args.max_steps)


if __name__ == "__main__":
    asyncio.run(main())
