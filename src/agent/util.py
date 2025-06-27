from browser_use.browser.browser import Browser
from typing import Dict, List
import imageio
import numpy as np
from playwright.sync_api import Page, BrowserContext
from PyPDF2 import PdfMerger
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64


def get_browser_context(browser: Browser) -> BrowserContext:
    context = browser.playwright_browser.contexts[0]
    return context


def get_pages(browser: Browser) -> List[Page]:
    context = browser.playwright_browser.contexts[0]
    pages = context.pages
    return pages


def get_page(browser: Browser) -> Page:
    return get_pages(browser)[0]


async def save_pages(
    pages: List[Page], output_dir: str, prefix: str = "temp_"
) -> List[str]:
    temp_pdfs = []
    for i, page in enumerate(pages):
        temp_pdf = os.path.join(output_dir, f"{prefix}{i}.pdf")
        await page.pdf(path=str(temp_pdf))
        temp_pdfs.append(temp_pdf)
    return temp_pdfs


def merge_pdfs(pdf_paths: List[str], output_path: str) -> None:
    # Merge PDFs using PyPDF2
    merger = PdfMerger()
    for pdf_path in pdf_paths:
        merger.append(pdf_path)

    # Write the merged PDF
    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()


def remove_files(file_paths: List[str]) -> None:
    for file_path in file_paths:
        os.remove(file_path)


def screenshot_to_numpy_array(
    screenshot_base64: str, text_area_height: int, entry: Dict
) -> np.ndarray:
    """Process a base64 screenshot into a PIL Image with text overlay and return as numpy array."""
    font_size = 20
    font = ImageFont.load_default(size=font_size)
    margin = 10

    # Decode the screenshot
    image_data = base64.b64decode(screenshot_base64)
    screenshot = Image.open(BytesIO(image_data)).convert("RGB")

    # Create a new image with additional space at the bottom for text
    width, height = screenshot.size
    new_image = Image.new("RGB", (width, height + text_area_height), (255, 255, 255))

    # Paste the screenshot at the top
    new_image.paste(screenshot, (0, 0))

    # Draw a separator line
    draw = ImageDraw.Draw(new_image)
    draw.line([(0, height), (width, height)], fill=(200, 200, 200), width=2)

    # Get overlay text
    text_lines = []
    model_output = entry.get("model_output", {})
    if "current_state" in model_output:
        text_lines.append("Goal: " + model_output["current_state"].get("next_goal", ""))

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
            text_height = int(font.getbbox(line_text)[3] - font.getbbox(line_text)[1])
            y += text_height + 5

    # Convert PIL Image to numpy array for imageio
    return np.array(new_image)


def save_to_png(screenshot_np: np.ndarray, image_path: str):
    imageio.imwrite(image_path, screenshot_np)


def save_to_gif(
    screenshots_np: List[np.ndarray],
    gif_path: str,
    images_dir: str,
    GIF_DURATION: int = 100,
):
    if screenshots_np:
        try:
            with open(str(gif_path), "wb") as f:
                imageio.mimwrite(f, screenshots_np, format="GIF", duration=GIF_DURATION)
            print(f"GIF saved to {gif_path}")
            print(f"Individual images saved to {images_dir}")
        except Exception as e:
            print(f"Failed to save GIF: {e}")
    else:
        print("No frames were created.")
