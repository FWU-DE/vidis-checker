import json
import os
from typing import List, Dict, Any, Set

from pydantic import BaseModel

from ..models.models import StepResult


class SingleTrackingPixelIssue(BaseModel):
    url: str
    explanation: str


class TrackingPixelIssues(BaseModel):
    issues: List[SingleTrackingPixelIssue]


def _read_network_requests(
    network_requests_path: str,
) -> List[Dict[str, Any]]:
    """
    Helper function to read network requests from a JSON file.

    Args:
        network_requests_path: Path to the JSON file containing network requests

    Returns:
        List of network request data
    """
    if not os.path.exists(network_requests_path):
        return []

    try:
        with open(network_requests_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading network requests from {network_requests_path}: {e}")
        return []


def check_for_tracking_pixels(step_result: StepResult) -> TrackingPixelIssues:
    """
    Check for tracking pixels in the step result resources

    Args:
        step_result: StepResult object containing resources and network requests

    Returns:
        TrackingPixelIssues object with identified tracking pixel issues
    """
    issues: List[SingleTrackingPixelIssue] = []
    processed_urls: Set[str] = set()

    # Process resources for tracking pixels
    for resource in step_result.resources:
        # Check for tiny images (tracking pixels)
        if (
            resource.type == "img"
            and resource.width is not None
            and resource.width <= 2
            and resource.height is not None
            and resource.height <= 2
        ):
            width = resource.width
            height = resource.height
            resource_url = resource.url

            # Only add if we haven't seen this URL before
            if resource_url not in processed_urls:
                issues.append(
                    SingleTrackingPixelIssue(
                        url=resource_url,
                        explanation=f"Image with size {width}x{height} pixels is suspicious as a tracking pixel",
                    )
                )
                processed_urls.add(resource_url)

    # Process network requests for suspicious image requests
    for pair in step_result.request_response_pairs:
        request = pair.request
        if request.resource_type == "image":
            request_url = request.url

            # Only add if we haven't seen this URL before and it's not already identified
            if request_url not in processed_urls:
                # We don't have size information in the request, so we make a general note
                issues.append(
                    SingleTrackingPixelIssue(
                        url=request_url,
                        explanation="Network request for image resource that might be a tracking pixel",
                    )
                )
                processed_urls.add(request_url)

    return TrackingPixelIssues(issues=issues)
