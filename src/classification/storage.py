from typing import List, Dict, Any

from ..models.models import StepResult

from .util import generate_structured_completion
from pydantic import BaseModel


def get_local_storage_entries(step_result: StepResult) -> Dict[str, Any]:
    """
    Extract local storage entries from browser data log file.

    Args:
        step_result: StepResult object containing browser data

    Returns:
        Dictionary mapping storage keys to their values and metadata
    """
    entries = step_result.local_storage.entries
    storage_entries = {}

    for key, value in entries.items():
        storage_entries[key] = {"value": value, "url": step_result.url}

    return storage_entries


def get_session_storage_entries(step_result: StepResult) -> Dict[str, Any]:
    """
    Extract session storage entries from browser data log file.

    Args:
        step_result: StepResult object containing browser data

    Returns:
        Dictionary mapping storage keys to their values and metadata
    """
    entries = step_result.session_storage.entries
    storage_entries = {}

    for key, value in entries.items():
        storage_entries[key] = {"value": value, "url": step_result.url}

    return storage_entries


class StorageEntryLLMResult(BaseModel):
    explanation: str
    is_essential: bool


class SingleStorageEntryCheckResult(BaseModel):
    key: str
    value: str
    url: str
    is_essential: bool
    explanation: str


class StorageCheckResult(BaseModel):
    results: List[SingleStorageEntryCheckResult]


storage_prompt = """
We need to determine if this browser storage entry is essential or non-essential for website functionality:

Storage Key: $KEY
Storage Value: $VALUE
Website URL: $URL

Essential storage entries are strictly necessary for basic website functionality (like keeping users logged in, 
remembering items in a shopping cart, or maintaining critical state information).

Non-essential storage entries are used for analytics, marketing, personalization, or enhanced functionality 
that isn't required for the basic operation of the website.

Based on this information, is this storage entry essential or non-essential? Provide your classification and reasoning.
"""


def check_storage_entry_essentiality(
    key: str, value: str, url: str
) -> StorageEntryLLMResult:
    """
    Check if a storage entry is essential using LLM.

    Args:
        key: Storage entry key
        value: Storage entry value
        url: URL where the storage entry was found

    Returns:
        LLM result with explanation and essentiality classification
    """
    prompt = (
        storage_prompt.replace("$KEY", key)
        .replace("$VALUE", str(value))
        .replace("$URL", url)
    )

    return generate_structured_completion(prompt, StorageEntryLLMResult)


def _check_storage_entries(entries: Dict[str, Any]) -> StorageCheckResult:
    """
    Helper function to check storage entries using LLM.

    Args:
        entries: Dictionary mapping storage keys to their values and metadata

    Returns:
        List of storage entry check results
    """
    storage_entries: List[SingleStorageEntryCheckResult] = []

    for key, data in entries.items():
        value = data["value"]
        url = data["url"]

        # Check essentiality using LLM
        llm_result = check_storage_entry_essentiality(key, value, url)

        storage_entries.append(
            SingleStorageEntryCheckResult(
                key=key,
                value=value,
                url=url,
                is_essential=llm_result.is_essential,
                explanation=llm_result.explanation,
            )
        )

    return StorageCheckResult(results=storage_entries)


def check_local_storage_entries(step_result: StepResult) -> StorageCheckResult:
    """
    Check if local storage contains only essential entries using LLM.

    Args:
        step_result: StepResult object containing browser data

    Returns:
        StorageCheckResult object with check results
    """
    entries = get_local_storage_entries(step_result)
    check_results = _check_storage_entries(entries)

    return check_results


def check_session_storage_entries(step_result: StepResult) -> StorageCheckResult:
    """
    Check if session storage contains only essential entries using LLM.

    Args:
        step_result: StepResult object containing browser data

    Returns:
        StorageCheckResult object with check results
    """
    entries = get_session_storage_entries(step_result)
    check_results = _check_storage_entries(entries)

    return check_results
