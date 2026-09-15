from typing import List, Optional

class TokenPayload(BaseModel):
    sub: str
    user_id: Optional[str] = None
    type: str                        # "access" | "refresh"
    exp: datetime
    iat: datetime
    jti: str
    scopes: List[str] = []