from typing import List, Type, TypeVar
from openai import OpenAI
import PyPDF2
from urllib.parse import urlparse

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


def read_text_from_pdf(path: str) -> str:
    with open(path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


if __name__ == "__main__":
    step_results = read_step_result_file("agent_results/schooltogo_login/step_result.jsonl")
    print(step_results[-1].cookies)
