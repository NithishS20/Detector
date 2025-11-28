from pydantic import BaseModel, Field
from typing import List, Optional


class LoginEvent(BaseModel):
    site: str
    username: str
    device_fingerprint: Optional[str] = None
    typing_speed: Optional[float] = None
    location: Optional[str] = None
    access_time: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    additional: Optional[dict] = Field(default_factory=dict)

class ProfileCreate(BaseModel):
    site: str
    username: str
    events: List[LoginEvent]

class CheckResult(BaseModel):
    suspicious: bool
    similarity: float
    reasons: List[str] = []
    forwarded: bool = False

