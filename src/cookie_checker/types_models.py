import json
from typing import Dict, List, Any, Optional, Union
from colorama import Fore, Style, init
from pydantic import BaseModel, Field

init()


class BaseChecker:
    """Base class for all checkers with common functionality"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def load_json_data(file_path: str) -> Any:
        """Load data from a JSON file"""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error parsing JSON in {file_path}")
            return None
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return None

    def print_success(self, message: str) -> None:
        print(f"{Fore.GREEN}[✓] {message}{Style.RESET_ALL}")

    def print_failure(self, message: str) -> None:
        print(f"{Fore.RED}[✗] {message}{Style.RESET_ALL}")

    def print_info(self, message: str) -> None:
        print(f"{Fore.BLUE}[i] {message}{Style.RESET_ALL}")


class CookieEntry(BaseModel):
    """Type definition for a cookie entry in the browser data log"""

    name: str
    domain: str
    path: str
    expires: float
    httpOnly: bool
    secure: bool
    sameSite: str
    value: str


class ResourceEntry(BaseModel):
    """Type definition for a resource entry in the browser data log"""

    url: str
    type: str
    width: int
    height: int
    src: str
    timestamp: float


class BrowserDataLogEntry(BaseModel):
    """Type definition for a single entry in the browser_data_log.jsonl file"""

    url: str
    cookies_and_origins: Dict[str, List[Dict[str, Any]]]
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    resources: List[Dict[str, Any]]


class NetworkRequest(BaseModel):
    """Type definition for a network request entry"""

    url: str
    resource_type: str
    method: str
    status: int
    headers: Dict[str, str]
    request_id: str
    time: float


class CookieDetails(BaseModel):
    domain: Optional[str] = None
    path: Optional[str] = None
    expires: Optional[float] = None
    httpOnly: bool = False
    secure: bool = False
    sameSite: Optional[str] = None
    value: Optional[str] = None


class CookieIssue(BaseModel):
    type: str
    name: str
    domain: Optional[str] = None
    path: Optional[str] = None
    details: CookieDetails


class Resource(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class TrackingIssue(BaseModel):
    type: str
    url: str
    resource: Resource


class RequestIssue(BaseModel):
    type: str
    url: str
    request: Dict[str, Any]


class CrossPageTracker(BaseModel):
    tracker_url: str
    page_count: int
    pages: List[str]


class TrackingAnalysis(BaseModel):
    cross_page_trackers: List[CrossPageTracker] = Field(default_factory=list)
    has_cross_page_tracking: bool = False


class FolderResult(BaseModel):
    folder: str
    file: str
    issues: List[Union[TrackingIssue, RequestIssue]]
    cross_page_tracking: bool
    cross_page_analysis: TrackingAnalysis


class UnauthorizedEntry(BaseModel):
    url: str
    key: str
    value: Any


class StorageViolation(BaseModel):
    folder: str
    file: str
    unauthorized: List[UnauthorizedEntry]


class CookieResult(BaseModel):
    folder: str
    file: str
    issues: List[CookieIssue]


class CheckResults(BaseModel):
    tracking_results: List[FolderResult] = Field(default_factory=list)
    local_storage_violations: List[StorageViolation] = Field(default_factory=list)
    session_storage_violations: List[StorageViolation] = Field(default_factory=list)
    cross_page_tracking_found: bool = False
    unique_tracking_pixels: List[str] = Field(default_factory=list)
    unique_suspicious_resources: List[str] = Field(default_factory=list)
    unique_suspicious_requests: List[str] = Field(default_factory=list)
    unique_unnecessary_cookies: List[str] = Field(default_factory=list)
    encryption_results: Dict[str, bool] = Field(default_factory=dict)
    overall_passed: bool = True
