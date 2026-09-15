"""
Authentication & authorization layer:
- Current-user extraction from Bearer tokens
- Role / scope based access control
- FastAPI dependencies
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import TokenPayload, decode_token
from app.domain.identity.models import User
from app.domain.identity.service import IdentityService


# ============================================================
# OAuth2 scheme (points to /api/v1/auth/login)
# ============================================================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
)


# ============================================================
# Roles & scopes
# ============================================================
class Role(str, Enum):
    ADMIN = "admin"
    ISSUER = "issuer"           # can issue credentials
    VERIFIER = "verifier"       # can verify credentials
    OPERATOR = "operator"       # can enroll users
    USER = "user"


class Scope(str, Enum):
    READ = "read"
    WRITE = "write"
    ISSUE = "credential:issue"
    VERIFY = "credential:verify"
    ENROLL = "identity:enroll"


# ============================================================
# Credentials
# ============================================================
class AuthError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
# Dependencies
# ============================================================
async def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPayload:
    """Extract & validate the access token payload."""
    try:
        return decode_token(token, expected_type="access")
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.PyJWTError:
        raise AuthError()


async def get_current_user(
    payload: Annotated[TokenPayload, Depends(get_token_payload)],
    identity_service: Annotated[IdentityService, Depends()],
) -> User:
    """Load the User object from the token's subject."""
    user = await identity_service.get_user_by_id(payload.sub)
    if user is None:
        raise AuthError("User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Alias — kept for readability in routers."""
    return user


# ============================================================
# Scope / role guards
# ============================================================
def require_scopes(*required: Scope):
    """Dependency factory: require ALL given scopes."""
    required_values = {s.value for s in required}

    async def _guard(
        payload: Annotated[TokenPayload, Depends(get_token_payload)],
    ) -> TokenPayload:
        user_scopes = set(payload.scopes or [])
        missing = required_values - user_scopes
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing scopes: {sorted(missing)}",
            )
        return payload

    return _guard


def require_roles(*required: Role):
    """Dependency factory: require ANY of the given roles."""
    required_values = {r.value for r in required}

    async def _guard(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        user_roles = set(getattr(user, "roles", []) or [])
        if not (required_values & user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {sorted(required_values)}",
            )
        return user

    return _guard


# ============================================================
# Type aliases for routers (cleaner signatures)
# ============================================================
CurrentUser = Annotated[User, Depends(get_current_active_user)]
TokenInfo = Annotated[TokenPayload, Depends(get_token_payload)]

RequireIssue = Annotated[User, Depends(require_roles(Role.ISSUER, Role.ADMIN))]
RequireVerify = Annotated[User, Depends(require_roles(Role.VERIFIER, Role.ADMIN))]
RequireEnroll = Annotated[User, Depends(require_roles(Role.OPERATOR, Role.ADMIN))]