from typing import Dict, List, Optional
from pydantic import BaseModel



class Cookie(BaseModel):
    name: str
    value: str
    domain: str
    path: str
    expires: float
    httpOnly: bool
    secure: bool
    sameSite: str

class LocalStorage(BaseModel):
    entries: Dict[str, str]

class SessionStorage(BaseModel):
    entries: Dict[str, str]

class Resource(BaseModel):
    type: str
    url: str
    width: Optional[int]
    height: Optional[int]
    id: Optional[str]
    className: Optional[str]


class NetworkRequest(BaseModel):
    url: str
    method: str
    headers: Dict[str, str]
    resource_type: str
    task_name: str
    timestamp: float
    post_data: Optional[str] = None

class NetworkResponse(BaseModel):
    url: str
    headers: Dict[str, str]
    status: int
    text: Optional[str] = None

class NetworkRequestResponsePair(BaseModel):
    request: NetworkRequest
    response: NetworkResponse

class StepResult(BaseModel):
    url: str
    cookies: List[Cookie]
    local_storage: LocalStorage
    session_storage: SessionStorage
    resources: List[Resource]
    request_response_pairs: List[NetworkRequestResponsePair]