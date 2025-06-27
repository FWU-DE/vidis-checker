import base64
import json
import os
import sys
import time
from io import BytesIO
from typing import Dict, List, Optional, Callable

from src.files.zip import create_zip_archive
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from PyPDF2 import PdfMerger

from .js_code import (
    LOCAL_STORAGE_CODE,
    SESSION_STORAGE_CODE,
    RESOURCES_CODE,
    SCROLL_TO_BOTTOM_CODE,
)
from .util import (
    get_browser_context,
    get_page,
    get_pages,
    merge_pdfs,
    save_to_gif,
    save_to_png,
    screenshot_to_numpy_array,
    remove_files,
    save_pages,
)
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
from langchain_core.messages import HumanMessage

from src.models.models import (
    Cookie,
    LocalStorage,
    NetworkRequest,
    NetworkRequestResponsePair,
    NetworkResponse,
    PageTypes,
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
AGENT_OUTPUT_DIR = "./agent_results"
GIF_DURATION = 2500.0


AZURE_MODEL = os.getenv("AZURE_MODEL", "fwuBMI_gpt-4.1")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT", "https://fwubmi.openai.azure.com/")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")
AZURE_API_KEY = os.getenv("OPENAI_API_KEY")

COOKIE_BANNER_JPG_FILENAME = "cookie_banner.jpg"
COOKIE_BANNER_JSON_FILENAME = "cookie_banner.json"


class VidisAgent:
    def __init__(
        self,
        task_prompt: str,
        initial_url: str,
        output_name: str,
        username: str,
        password: str,
        headless: bool = True,
        disable_security: bool = True,
        minimum_wait_page_load_time: int = 2,
        maximum_wait_page_load_time: int = 15,
    ):
        self.username = username
        self.password = password
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
        self.controller = Controller(exclude_actions=["search_google"])
        self.llm = AzureChatOpenAI(
            model=AZURE_MODEL,
            azure_endpoint=AZURE_ENDPOINT,
            api_version=AZURE_API_VERSION,
            api_key=AZURE_API_KEY,
        )
        self.visited_pages: List[str] = []
        self.register_actions()
        self.request_response_pairs: List[NetworkRequestResponsePair] = []
        self.request_listener: Optional[Callable] = None
        self.task_prompt = task_prompt
        self.output_name = output_name
        self.seen_legal_pages: List[str] = []
        self.initial_url = initial_url
        os.makedirs(AGENT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.join(AGENT_OUTPUT_DIR, output_name), exist_ok=True)

    def register_actions(self):
        """Register custom actions with the controller."""

        @self.controller.action(
            "Save the page of type: page_type (privacy_policy, imprint, terms_of_use, register, logout) as pdf in the current task folder",
            param_model=PageTypes,
        )
        async def save_page_as_pdf(page_type: PageTypes) -> ActionResult:
            try:
                if page_type.page_type not in self.seen_legal_pages:
                    pages = get_pages(self.browser)
                    output_dir = os.path.join(AGENT_OUTPUT_DIR, self.output_name)
                    os.makedirs(output_dir, exist_ok=True)

                    pdf_filename = f"{page_type.page_type}.pdf"
                    pdf_path = os.path.join(output_dir, pdf_filename)

                    # Save each page as a separate PDF temporarily
                    temp_pdfs = await save_pages(pages, output_dir)

                    merge_pdfs(temp_pdfs, pdf_path)

                    # Clean up temporary PDFs
                    remove_files(temp_pdfs)

                    self.seen_legal_pages.append(page_type.page_type)

                    return ActionResult(
                        extracted_content=f"{page_type.page_type} Pages saved as PDF: {pdf_path}",
                        include_in_memory=True,
                    )
                else:
                    return ActionResult(
                        extracted_content=f"{page_type.page_type} Page already saved",
                        include_in_memory=True,
                    )
            except Exception as e:
                return ActionResult(
                    error=f"Failed to save pages as PDF: {str(e)}",
                    include_in_memory=True,
                )

        @self.controller.action("Scroll to bottom of the page")
        async def scroll_to_bottom() -> ActionResult:
            try:
                page = get_page(self.browser)
                await page.evaluate(SCROLL_TO_BOTTOM_CODE)
                return ActionResult(extracted_content="Scrolled to bottom of the page.")
            except Exception as e:
                return ActionResult(error=f"Failed to scroll: {str(e)}")

        @self.controller.action("cookie_handler: save the cookies as screenshots")
        async def cookie_handler() -> ActionResult:
            try:
                page = get_page(self.browser)

                page_url = page.url

                output_dir = os.path.join(AGENT_OUTPUT_DIR, self.output_name)
                screenshot_path = os.path.join(output_dir, COOKIE_BANNER_JPG_FILENAME)

                screenshot_bytes = await page.screenshot()
                image = Image.open(BytesIO(screenshot_bytes))
                image.save(screenshot_path, "JPEG", quality=85)

                data = {
                    "url": page_url,
                    "timestamp": int(time.time()),
                    "screenshot_filename": COOKIE_BANNER_JPG_FILENAME,
                    "screenshot_path": str(screenshot_path),
                }

                with open(
                    os.path.join(output_dir, COOKIE_BANNER_JSON_FILENAME),
                    "a",
                    encoding="utf-8",
                ) as f:
                    f.write(json.dumps(data) + "\n")

                return ActionResult(extracted_content="Cookies saved successfully.")
            except Exception as e:
                return ActionResult(error=f"Failed to save cookies: {str(e)}")

    def setup_network_tracking(self, context: BrowserContext):
        """Set up network request tracking for the browser context."""

        async def on_response(response) -> None:
            request = response.request

            request_data = NetworkRequest(
                url=request.url,
                method=request.method,
                headers=request.headers,
                resource_type=request.resource_type,
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

    async def on_step_start(self, agent_obj: Agent) -> ActionResult:
        agent_obj.message_manager._add_message_with_tokens(
            HumanMessage(
                content=f"Visited pages: {self.visited_pages}, Already saved legal pages: {self.seen_legal_pages}, Amount of unique pages: {len(self.visited_pages)}"
            )
        )
        return ActionResult(
            extracted_content=f"Visited pages: {self.visited_pages}, Already saved legal pages: {self.seen_legal_pages}, Amount of unique pages: {len(self.visited_pages)}",
            include_in_memory=True,
        )

    async def on_step_end(self, agent_obj) -> None:
        """Collect current browser data including cookies, local storage, and session storage."""
        try:
            context = get_browser_context(self.browser)

            # Set up network tracking on first call
            if not hasattr(self, "request_listener") or self.request_listener is None:
                print("First step: setting up network tracking...")
                self.request_listener = self.setup_network_tracking(context)

            page = context.pages[0]
            url = page.url
            if url not in self.visited_pages:
                self.visited_pages.append(url)

            cookies = await context.cookies()

            local_storage = await page.evaluate(LOCAL_STORAGE_CODE)
            session_storage = await page.evaluate(SESSION_STORAGE_CODE)
            resources_raw = await page.evaluate(RESOURCES_CODE)

            resources = [Resource.model_validate(item) for item in resources_raw]

            step_result = StepResult(
                url=url,
                cookies=[Cookie.model_validate(cookie) for cookie in cookies],
                local_storage=LocalStorage(entries=local_storage),
                session_storage=SessionStorage(entries=session_storage),
                resources=resources,
                request_response_pairs=self.request_response_pairs,
            )

            # Clear network request response pairs after each step
            self.request_response_pairs = []

            output_dir = os.path.join(AGENT_OUTPUT_DIR, self.output_name)
            with open(
                os.path.join(output_dir, "step_result.jsonl"), "a", encoding="utf-8"
            ) as f:
                f.write(json.dumps(step_result.model_dump()) + "\n")
            return
        except Exception as e:
            print(f"Failed to retrieve browser data: {str(e)}")
            return

    def create_gif_from_history(self, history_data: List[Dict], output_name: str):
        """Create an animated GIF from the agent's history with text in a dedicated bottom area."""
        screenshots_np = []
        output_dir = os.path.join(AGENT_OUTPUT_DIR, output_name)
        gif_path = os.path.join(output_dir, f"animation.gif")

        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        text_area_height = 150

        for i, entry in enumerate(history_data):
            screenshot_base64 = entry.get("state", {}).get("screenshot", "")
            if not screenshot_base64:
                continue

            try:
                screenshot_np = screenshot_to_numpy_array(
                    screenshot_base64, text_area_height, entry
                )
                screenshots_np.append(screenshot_np)

                image_name = f"step_{i:03d}.png"
                image_path = os.path.join(images_dir, image_name)
                save_to_png(screenshot_np, image_path)

            except Exception as e:
                print(f"Failed to process screenshot: {e}")
                continue

        save_to_gif(screenshots_np, gif_path, images_dir, GIF_DURATION)

    async def run_task(self, max_steps: int = 25):
        """Run the task."""
        output_dir = os.path.join(AGENT_OUTPUT_DIR, self.output_name)
        os.makedirs(output_dir, exist_ok=True)

        initial_actions = [{"go_to_url": {"url": self.initial_url}}]

        sensitive_data = {
            "VIDIS_USERNAME": self.username,
            "VIDIS_PASSWORD": self.password,
        }

        agent = Agent(
            task=self.task_prompt,
            llm=self.llm,
            browser=self.browser,
            validate_output=True,
            controller=self.controller,
            initial_actions=initial_actions,
            enable_memory=True,
            sensitive_data=sensitive_data,
        )

        history = await agent.run(
            on_step_start=self.on_step_start,
            on_step_end=self.on_step_end,
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
        output_dir = os.path.join(AGENT_OUTPUT_DIR, output_name)

        zip_filename = f"{output_name}.zip"
        zip_path = os.path.join(AGENT_OUTPUT_DIR, zip_filename)

        create_zip_archive(str(output_dir), str(zip_path))
        print(f"Created zip archive at: {zip_path}")
