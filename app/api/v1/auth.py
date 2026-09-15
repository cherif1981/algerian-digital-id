from typing import List, Optional
from pydantic import BaseModel, EmailStr


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
    all_devices: bool = False


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    roles: List[str] = []
    scopes: List[str] = []


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int