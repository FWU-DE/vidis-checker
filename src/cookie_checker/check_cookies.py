import json
import os
from typing import List, Dict, Any, Optional, Tuple, Union

from .types_models import (
    CookieIssue,
    CookieDetails,
    TrackingIssue,
    RequestIssue,
    TrackingAnalysis,
    CrossPageTracker,
    UnauthorizedEntry,
    Resource,
    BrowserDataLogEntry,
    BaseChecker,
)


class CookieChecker(BaseChecker):
    """Checks for cookie-related privacy issues"""

    def __init__(self) -> None:
        super().__init__()

    def check_cookies(self, browser_data_path: str) -> List[CookieIssue]:
        """
        Check for cookies in browser data log
        """
        issues: List[CookieIssue] = []

        with open(browser_data_path, "r") as f:
            seen_cookies: Dict[str, CookieDetails] = {}
            for line in f:
                try:
                    raw_data = json.loads(line.strip())
                    try:
                        data = BrowserDataLogEntry(**raw_data)
                    except Exception as e:
                        print(f"Invalid browser data log format: {e}")
                        continue
                    if not data:
                        continue
                    cookies: List[Dict[str, Any]] = data.cookies_and_origins.get(
                        "cookies", []
                    )
                    for cookie in cookies:
                        # Ensure cookie is a dictionary with type annotation
                        cookie_name = cookie.get("name")
                        if cookie_name:
                            # Store cookie with its details
                            if cookie_name not in seen_cookies:
                                seen_cookies[cookie_name] = CookieDetails(
                                    domain=cookie.get("domain"),
                                    path=cookie.get("path"),
                                    expires=cookie.get("expires"),
                                    httpOnly=cookie.get("httpOnly", False),
                                    secure=cookie.get("secure", False),
                                    sameSite=cookie.get("sameSite"),
                                    value=cookie.get("value"),
                                )
                except json.JSONDecodeError:
                    print(f"Error parsing JSON line in {browser_data_path}")
                    continue
                except Exception as e:
                    print(f"Error processing line in {browser_data_path}: {e}")
                    continue

            # Check if cookies are necessary
            for cookie_name, details in seen_cookies.items():
                # Check if it's a necessary cookie (session, CSRF, etc.)
                if not self._is_necessary_cookie(cookie_name):
                    issues.append(
                        CookieIssue(
                            type="unnecessary_cookie",
                            name=cookie_name,
                            domain=details.domain,
                            path=details.path,
                            details=details,
                        )
                    )

            return issues

    @staticmethod
    def _is_necessary_cookie(cookie_name: str) -> bool:
        """Check if a cookie is necessary for site functionality"""
        cookie_lower = cookie_name.lower()
        necessary_terms = [
            "session",
            "csrf",
            "xsrf",
            "_token",
            "oauth",
            "cookieconsent",
            "cookiebot",
        ]
        necessary_names = ["jsessionid", "phpsessid", "aspsessionid"]

        # Check for terms within the cookie name
        for term in necessary_terms:
            if term in cookie_lower:
                return True

        # Check for exact matches with known necessary cookies
        if cookie_lower in necessary_names:
            return True

        return False


class TrackingChecker(BaseChecker):
    """Checks for tracking pixels and other tracking mechanisms"""

    def __init__(self) -> None:
        super().__init__()

    def check_for_tracking_pixels(
        self, browser_data_path: str, network_requests_path: Optional[str] = None
    ) -> List[Union[TrackingIssue, RequestIssue]]:
        """
        Check for tracking pixels in browser data log and network requests

        Args:
            browser_data_path: Path to the browser_data_log.jsonl file
            network_requests_path: Path to the network_requests.json file (optional)

        Returns:
            List of identified tracking issues
        """
        issues: List[Union[TrackingIssue, RequestIssue]] = []

        # Process browser_data_log.jsonl for tracking pixels
        with open(browser_data_path, "r") as f:
            for line in f:
                try:
                    raw_data = json.loads(line.strip())
                    try:
                        data = BrowserDataLogEntry(**raw_data)
                    except Exception as e:
                        print(f"Invalid browser data log format: {e}")
                        continue
                    resources: List[Dict[str, Any]] = data.resources
                    page_url: str = data.url
                    for resource in resources:
                        # Check for tiny images (tracking pixels)
                        if (
                            resource.get("type") == "img"
                            and resource.get("width", 0) <= 3
                            and resource.get("height", 0) <= 3
                        ):
                            issues.append(
                                TrackingIssue(
                                    type="tracking_pixel",
                                    url=page_url,
                                    resource=Resource(**resource),
                                )
                            )

                        # Check for suspicious URLs
                        url_lower = resource.get("url", "").lower()
                        if self._is_suspicious_resource_url(url_lower):
                            issues.append(
                                TrackingIssue(
                                    type="suspicious_resource",
                                    url=page_url,
                                    resource=Resource(**resource),
                                )
                            )
                except json.JSONDecodeError:
                    print(f"Error parsing JSON line in {browser_data_path}")
                    continue
                except Exception as e:
                    print(f"Error processing line in {browser_data_path}: {e}")
                    continue

        # Process network_requests.json for suspicious requests if provided
        if network_requests_path and os.path.exists(network_requests_path):
            requests: List[Dict[str, Any]] = self.load_json_data(network_requests_path)
            if requests:
                for request in requests:
                    if request.get("resource_type") in [
                        "image",
                        "fetch",
                        "xhr",
                        "beacon",
                    ]:
                        parsed_url = request.get("url", "").lower()
                        if self._is_suspicious_network_url(parsed_url):
                            issues.append(
                                RequestIssue(
                                    type="suspicious_request",
                                    url=request.get("url", "Unknown"),
                                    request=request,
                                )
                            )

        return issues

    @staticmethod
    def _is_suspicious_resource_url(url: str) -> bool:
        """Check if a resource URL appears to be for tracking purposes"""
        suspicious_terms = ["analytics", "track", "pixel", "beacon", "counter"]
        return any(tracker in url for tracker in suspicious_terms)

    @staticmethod
    def _is_suspicious_network_url(url: str) -> bool:
        """Check if a network request URL appears to be for tracking purposes"""
        suspicious_terms = [
            "track",
            "pixel",
            "analytics",
            "collect",
            "beacon",
            "telemetry",
            "metric",
            "piwik",
            "ga.js",
            "gtm.js",
            "fbevents",
            "insight",
            "consent",
        ]
        return any(term in url for term in suspicious_terms)


class TrackingAnalyzer(BaseChecker):
    """Analyzes tracking results to identify patterns and cross-page tracking"""

    def __init__(self) -> None:
        super().__init__()

    def analyze_tracking(
        self, tracking_results: List[Union[TrackingIssue, RequestIssue]]
    ) -> TrackingAnalysis:
        """
        Analyze tracking pixel results to determine if the same tracking pixel
        is used across multiple pages, which indicates cross-page tracking.

        Args:
            tracking_results: List of tracking issues from check_for_tracking_pixels

        Returns:
            Analysis results containing cross-page trackers and affected pages
        """
        if not tracking_results:
            return TrackingAnalysis(
                cross_page_trackers=[],
                has_cross_page_tracking=False,
            )

        # Extract tracking pixel issues
        tracking_pixels: List[TrackingIssue] = [
            i
            for i in tracking_results
            if i.type == "tracking_pixel" and isinstance(i, TrackingIssue)
        ]

        # Map tracking pixel URLs to the pages they appear on
        tracker_to_pages: Dict[str, List[str]] = {}
        for pixel in tracking_pixels:
            pixel_url = pixel.resource.url
            page_url = pixel.url

            if not pixel_url or not page_url:
                continue

            if pixel_url not in tracker_to_pages:
                tracker_to_pages[pixel_url] = []

            if page_url not in tracker_to_pages[pixel_url]:
                tracker_to_pages[pixel_url].append(page_url)

        # Find trackers that appear on multiple pages
        cross_page_trackers: List[CrossPageTracker] = []
        for tracker_url, pages in tracker_to_pages.items():
            if len(pages) > 1:
                cross_page_trackers.append(
                    CrossPageTracker(
                        tracker_url=tracker_url,
                        page_count=len(pages),
                        pages=pages,
                    )
                )

        return TrackingAnalysis(
            cross_page_trackers=cross_page_trackers,
            has_cross_page_tracking=len(cross_page_trackers) > 0,
        )


class StorageChecker(BaseChecker):
    """Checks for privacy-related storage issues (localStorage, sessionStorage)"""

    def __init__(self) -> None:
        super().__init__()

    def check_local_storage_entries(
        self, jsonl_file_path: str, allowed_entries: List[str]
    ) -> Tuple[bool, List[UnauthorizedEntry]]:
        """
        Check if local storage contains only the necessary entries in a JSONL file.
        Entries with prefixes in the allowed_entries list are also allowed.

        Args:
            jsonl_file_path: Path to the JSONL file containing browser data
            allowed_entries: List of entry keys that are allowed in local storage
                            (prefix matching enabled, e.g., "wc_card_hash_" will match "wc_card_hash_12345")

        Returns:
            tuple: (bool indicating if check passed, list of unauthorized entries found)
        """
        unauthorized_entries: List[UnauthorizedEntry] = []

        with open(jsonl_file_path, "r") as f:
            for line in f:
                try:
                    raw_data = json.loads(line.strip())
                    try:
                        data = BrowserDataLogEntry(**raw_data)
                    except Exception as e:
                        print(f"Invalid browser data log format: {e}")
                        continue
                    # Check if local_storage exists and is not empty
                    if data.local_storage and isinstance(data.local_storage, dict):
                        local_storage_keys = set(data.local_storage.keys())

                        # Check each key against allowed entries (including prefix matching)
                        for key in local_storage_keys:
                            # Check if the key is allowed exactly or as a prefix
                            is_allowed = key in allowed_entries or any(
                                key.startswith(allowed_prefix)
                                for allowed_prefix in allowed_entries
                            )

                            if not is_allowed:
                                unauthorized_entries.append(
                                    UnauthorizedEntry(
                                        url=data.url,
                                        key=key,
                                        value=data.local_storage[key],
                                    )
                                )
                except json.JSONDecodeError:
                    unauthorized_entries.append(
                        UnauthorizedEntry(
                            url="Unknown",
                            key="JSON_DECODE_ERROR",
                            value=f"Error parsing JSON line in {jsonl_file_path}",
                        )
                    )
                except Exception as e:
                    unauthorized_entries.append(
                        UnauthorizedEntry(
                            url="Unknown",
                            key="ERROR",
                            value=f"Error processing line: {str(e)}",
                        )
                    )

        return len(unauthorized_entries) == 0, unauthorized_entries

    def check_session_storage_entries(
        self, jsonl_file_path: str, allowed_entries: List[str]
    ) -> Tuple[bool, List[UnauthorizedEntry]]:
        """
        Check if session storage contains only the necessary entries in a JSONL file.
        Entries with prefixes in the allowed_entries list are also allowed.

        Args:
            jsonl_file_path: Path to the JSONL file containing browser data
            allowed_entries: List of entry keys that are allowed in session storage
                            (prefix matching enabled, e.g., "wc_card_hash_" will match "wc_card_hash_12345")

        Returns:
            tuple: (bool indicating if check passed, list of unauthorized entries found)
        """
        unauthorized_entries: List[UnauthorizedEntry] = []

        with open(jsonl_file_path, "r") as f:
            for line in f:
                try:
                    raw_data = json.loads(line.strip())
                    try:
                        data = BrowserDataLogEntry(**raw_data)
                    except Exception as e:
                        print(f"Invalid browser data log format: {e}")
                        continue

                    # Check if session_storage exists and is not empty
                    if data.session_storage and isinstance(data.session_storage, dict):
                        session_storage_keys = set(data.session_storage.keys())

                        # Check each key against allowed entries (including prefix matching)
                        for key in session_storage_keys:
                            # Check if the key is allowed exactly or as a prefix
                            is_allowed = key in allowed_entries or any(
                                key.startswith(allowed_prefix)
                                for allowed_prefix in allowed_entries
                            )

                            if not is_allowed:
                                unauthorized_entries.append(
                                    UnauthorizedEntry(
                                        url=str(data.url),
                                        key=key,
                                        value=data.session_storage[key],
                                    )
                                )
                except json.JSONDecodeError:
                    unauthorized_entries.append(
                        UnauthorizedEntry(
                            url="Unknown",
                            key="JSON_DECODE_ERROR",
                            value=f"Error parsing JSON line in {jsonl_file_path}",
                        )
                    )
                except Exception as e:
                    unauthorized_entries.append(
                        UnauthorizedEntry(
                            url="Unknown",
                            key="ERROR",
                            value=f"Error processing line: {str(e)}",
                        )
                    )

        return len(unauthorized_entries) == 0, unauthorized_entries
