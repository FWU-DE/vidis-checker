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

from src.tasks import get_all_tasks
from src.models import (
    TypedArgs,
    NetworkRequest,
    NetworkRequestHeaders,
    BrowserStorageData,
    ResourceItem,
)

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Global variables
WINDOW_SIZE = BrowserContextWindowSize(width=1280, height=1100)
OUTPUT_DIR = Path("./tmp")
GIF_DURATION = 3500.0


class BrowserAutomation:
    def __init__(self, tasks: List[Dict[str, Any]]):
        self.browser = self._setup_browser()
        self.controller = Controller()
        self.llm = self._setup_llm()
        self.register_actions()
        self.current_task_index = 0

        # Store network requests for the current task only
        self.network_requests: List[NetworkRequest] = []

        self.request_listener: Optional[Callable] = None

        self.tasks = tasks

    def _setup_llm(self):
        """Configure and return the appropriate LLM based on environment variables."""
        if os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(model="gpt-4o")
        else:
            raise ValueError(
                "No LLM found. Please set OPENAI_API_KEY or AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT."
            )

    def _setup_browser(self):
        """Configure and return the browser instance."""
        return Browser(
            config=BrowserConfig(
                headless=False,
                disable_security=True,
                new_context_config=BrowserContextConfig(
                    disable_security=True,
                    minimum_wait_page_load_time=2,
                    maximum_wait_page_load_time=15,
                    browser_window_size=WINDOW_SIZE,
                ),
            )
        )

    def register_actions(self):
        """Register custom actions with the controller."""

        @self.controller.action(
            "Save the page of type: page_type (privacy_policy, imprint, tos, register, logout) as pdf in the current task folder"
        )
        async def save_page_as_pdf(page_type: str) -> ActionResult:
            try:
                # Get the current page
                page = self.browser.playwright_browser.contexts[0].pages[0]
                task_name = self.tasks[self.current_task_index]["name"]
                pdf_dir: Path = OUTPUT_DIR / task_name
                pdf_dir.mkdir(parents=True, exist_ok=True)

                # Generate PDF file path
                # timestamp = int(time.time())
                pdf_filename = f"{page_type}.pdf"
                pdf_path = pdf_dir / pdf_filename

                # Save the page as PDF
                await page.pdf(path=str(pdf_path))

                return ActionResult(
                    extracted_content=f"{page_type} Page saved as PDF: {pdf_path}"
                )
            except Exception as e:
                return ActionResult(error=f"Failed to save page as PDF: {str(e)}")

        # @self.controller.action("Ask user for information or help")
        # def ask_human(question: str) -> ActionResult:
        #     answer = input(f"\n{question}\nInput: ")
        #     return ActionResult(extracted_content=answer)

        @self.controller.action("Scroll to bottom of the page")
        async def scroll_to_bottom() -> ActionResult:
            try:
                # Get the current page
                page = self.browser.playwright_browser.contexts[0].pages[0]
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                return ActionResult(extracted_content="Scrolled to bottom of the page.")
            except Exception as e:
                return ActionResult(error=f"Failed to scroll: {str(e)}")

        @self.controller.action("coockie_handler: save the cookies as screenshots")
        async def cookie_handler() -> ActionResult:
            try:
                # Get the current page
                page = self.browser.playwright_browser.contexts[0].pages[0]
                page_url = page.url

                # Generate random filename
                random_string = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=10)
                )
                timestamp = int(time.time())
                task_name = self.tasks[self.current_task_index]["name"]

                screenshot_filename = f"screenshot_{timestamp}_{random_string}.jpg"
                screenshot_dir = OUTPUT_DIR / task_name
                screenshot_path = screenshot_dir / screenshot_filename

                # Take screenshot and save as JPG
                screenshot_bytes = await page.screenshot()
                image = Image.open(BytesIO(screenshot_bytes))
                image.save(screenshot_path, "JPEG", quality=85)

                # Create data for logging
                data = {
                    "url": page_url,
                    "timestamp": timestamp,
                    "screenshot_filename": screenshot_filename,
                    "screenshot_path": str(screenshot_path),
                }

                # Append the data to cookies_banner.jsonl
                with open(
                    screenshot_dir / "cookies_banner.jsonl", "a", encoding="utf-8"
                ) as f:
                    f.write(json.dumps(data) + "\n")

                return ActionResult(extracted_content="Cookies saved successfully.")
            except Exception as e:
                return ActionResult(error=f"Failed to save cookies: {str(e)}")

    def setup_network_tracking(self, context: BrowserContext):
        """Set up network request tracking for the browser context."""

        async def on_request(request: Request) -> None:
            headers_dict = request.headers
            headers = NetworkRequestHeaders.model_validate(headers_dict)

            # Create request data model
            request_data = NetworkRequest(
                url=request.url,
                method=request.method,
                headers=headers,
                resource_type=request.resource_type,
                task_index=self.current_task_index,
                task_name=self.tasks[self.current_task_index]["name"],
                timestamp=time.time(),
            )

            # Try to capture post data if available
            try:
                post_data = request.post_data
                if post_data:
                    request_data.post_data = post_data
            except Exception:  # Use specific exception type instead of bare except
                pass

            self.network_requests.append(request_data)

        # Register the event listener
        context.on("request", on_request)

        return on_request

    async def get_browser_data(self, agent_obj) -> ActionResult:
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

            # Get cookies and storage data
            storage = await context.storage_state()

            # Get local storage
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

            # Get session storage
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

            # Collect network resources that may include tracking pixels
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

            # Parse resources using the ResourceItem model
            resources = [ResourceItem.model_validate(item) for item in resources_raw]

            # Get current network requests for this page
            task_name = self.tasks[self.current_task_index]["name"]
            current_page_requests = [
                req
                for req in self.network_requests
                if req.task_index == self.current_task_index
                and req.task_name == task_name
            ]

            # Prepare data for logging using the BrowserStorageData model
            browser_data = BrowserStorageData(
                url=url,
                timestamp=time.time(),
                cookies_and_origins=storage,
                local_storage=local_storage,
                session_storage=session_storage,
                resources=[resource.model_dump() for resource in resources],
                network_requests_count=len(current_page_requests),
            )

            # Save data to log file
            task_name = self.tasks[self.current_task_index]["name"]
            with open(
                OUTPUT_DIR / task_name / "browser_data_log.jsonl", "a", encoding="utf-8"
            ) as f:
                f.write(json.dumps(browser_data.model_dump()) + "\n")

            return ActionResult(extracted_content=browser_data.model_dump())
        except Exception as e:
            return ActionResult(error=f"Failed to retrieve browser data: {str(e)}")

    def create_gif_from_history(self, history_data: List[Dict], task_name: str):
        """Create an animated GIF from the agent's history with text in a dedicated bottom area."""
        frames = []
        gif_path = OUTPUT_DIR / task_name / f"history_animation_{task_name}.gif"

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

    async def run_task(self, task_index: int):
        """Run a specific task by index."""
        # Clear network requests from previous tasks
        self.network_requests = []

        self.current_task_index = task_index
        task_config = self.tasks[task_index]
        task_name = task_config["name"]

        # Create output directory with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        task_dir: Path = OUTPUT_DIR / task_name / timestamp
        task_dir.mkdir(parents=True, exist_ok=True)

        # Configure initial action to navigate to the URL
        initial_actions = [{"go_to_url": {"url": task_config["url"]}}]

        # Create and run the agent
        agent = Agent(
            task=task_config["task"],
            llm=self.llm,
            browser=self.browser,
            validate_output=True,
            controller=self.controller,
            initial_actions=initial_actions,
            enable_memory=True,
        )

        history = await agent.run(
            on_step_end=self.get_browser_data,
            max_steps=25,
        )

        # Save history to file
        history_path = task_dir / "history.json"
        history.save_to_file(str(history_path))

        # Remove the request listener after task completion if it was set
        if (
            hasattr(self, "request_listener")
            and self.request_listener
            and self.browser.playwright_browser
            and len(self.browser.playwright_browser.contexts) > 0
        ):
            context = self.browser.playwright_browser.contexts[0]
            context.remove_listener("request", self.request_listener)

        # Save network requests to a single JSON file
        network_requests_path = task_dir / "network_requests.json"
        try:
            formatted_requests = []
            for req in self.network_requests:
                # Create a clean copy of the request data using the model
                formatted_requests.append(req.model_dump())

            # Write all requests to a single JSON file
            with open(network_requests_path, "w", encoding="utf-8") as f:
                json.dump(formatted_requests, f, indent=2)

            print(
                f"Saved {len(formatted_requests)} requests to {network_requests_path}"
            )
        except Exception as e:
            print(f"Failed to save network requests to JSON file: {str(e)}")

        # Create GIF from history
        with open(history_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            self.create_gif_from_history(history_data["history"], task_name)

        # Create a zip file of the task directory
        self.create_zip_archive(task_name)

    async def run_all_tasks(self):
        """Run all defined tasks sequentially."""
        for i in range(len(self.tasks)):
            await self.run_task(i)

    def create_zip_archive(self, task_name: str):
        """Create a zip file of the task directory."""
        task_dir = OUTPUT_DIR / task_name
        zip_path = OUTPUT_DIR / f"{task_name}.zip"

        try:
            with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(str(task_dir)):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Don't include the zip file itself if it already exists
                        if file_path != str(zip_path):
                            # Calculate relative path to preserve directory structure
                            arcname = os.path.relpath(file_path, str(OUTPUT_DIR))
                            zipf.write(file_path, arcname)

            print(f"Created zip archive: {zip_path}")
        except Exception as e:
            print(f"Failed to create zip archive: {str(e)}")


async def main():
    parser = argparse.ArgumentParser(description="Crawl the web and save the data")
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=["all"],
        help="Run a specific task by name or 'all' to run all tasks. Options are legal, student, teacher, register, logout",
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the website to crawl",
    )
    args = parser.parse_args()
    typed_args = TypedArgs(**vars(args))
    tasks = get_all_tasks(typed_args.url, typed_args.tasks)
    automation = BrowserAutomation(tasks=tasks)
    await automation.run_all_tasks()


if __name__ == "__main__":
    asyncio.run(main())
