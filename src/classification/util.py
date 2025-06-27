import base64
from datetime import datetime
from typing import List, Type, TypeVar
import uuid
from openai import OpenAI
import PyPDF2
from urllib.parse import urlparse, unquote
import re

from ..models.models import StepResult


def read_step_result_file(path: str) -> List[StepResult]:
    with open(path, "r") as file:
        return [StepResult.model_validate_json(line) for line in file]


def extract_domain(url: str) -> str:
    """
    Extract domain from a URL.
    If URL doesn't have a scheme (http:// or https://), https:// is added
    by default.

    Args:
        url (str): URL to parse

    Returns:
        str: Domain extracted from the URL
    """
    # Make sure URL has scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Parse domain from URL
    parsed_url = urlparse(url)
    return parsed_url.netloc


def generate_completion(prompt: str) -> str:
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    return completion.choices[0].message.content


T = TypeVar("T")


def generate_structured_completion(prompt: str, response_format: Type[T]) -> T:
    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format=response_format,
    )

    return completion.choices[0].message.parsed


def analyze_image(
    image_path: str, response_format: Type[T], prompt: str = "What's in this image?"
) -> T:
    """
    Analyze an image using OpenAI's vision model.

    Args:
        image_path (str): Path to the image file
        response_format (Type[T]): Expected response format
        prompt (str): Text prompt for the analysis

    Returns:
        T: Analysis result from the model
    """

    client = OpenAI()

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    base64_image = encode_image(image_path)

    completion = client.beta.chat.completions.parse(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        response_format=response_format,
    )

    return completion.choices[0].message.parsed


def read_text_from_pdf(path: str) -> str:
    with open(path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


def url_to_dirname(url: str) -> str:
    """
    Convert a URL into a filesystem-safe directory name.

    - Parses the URL into scheme, netloc, path, and query.
    - URL-decodes percent-escapes.
    - Joins components with underscores.
    - Replaces illegal filesystem characters with underscores.
    - Optionally truncates the result to max_length characters.
    """
    # 1) Parse and decode
    parsed = urlparse(url)
    components = [
        parsed.scheme,
        parsed.netloc,
        unquote(parsed.path),
        unquote(parsed.query),
    ]
    # 2) Join non-empty components with underscore
    joined = "_".join(filter(None, components))
    # 3) Replace chars other than alphanum, dot, underscore, hyphen
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", joined).strip("_")
    return safe


def generate_dirname(url: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_uuid = str(uuid.uuid4())
    processed_url = url_to_dirname(url)
    return f"run_{processed_url}_{timestamp}_{random_uuid}"


if __name__ == "__main__":
    urls = ["https://schooltogo.de"]
    for u in urls:
        print(f"{u!r}  →  {generate_dirname(u)}")
