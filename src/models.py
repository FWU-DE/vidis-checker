from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TypedArgs(BaseModel):
    """Command line arguments typed model"""

    tasks: List[str]
    url: str


class NetworkRequestHeaders(BaseModel):
    """Model for HTTP request headers"""

    content_type: Optional[str] = Field(None, alias="content-type")
    user_agent: Optional[str] = Field(None, alias="user-agent")
    accept: Optional[str] = None
    referer: Optional[str] = None
    cookie: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "allow"


class NetworkRequest(BaseModel):
    """Model for network requests captured during browsing"""

    url: str
    method: str
    headers: NetworkRequestHeaders
    resource_type: str
    task_index: int
    task_name: str
    timestamp: float
    post_data: Optional[str] = None


class BrowserStorageData(BaseModel):
    """Model for browser storage data"""

    url: str
    timestamp: float
    cookies_and_origins: Dict[str, Any]
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    resources: List[Dict[str, Any]]
    network_requests_count: int


class ResourceItem(BaseModel):
    """Model for resources like images, iframes, scripts"""

    type: str
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    id: Optional[str] = None
    className: Optional[str] = None
