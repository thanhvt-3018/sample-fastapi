from __future__ import annotations

from fastapi import Cookie, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.error_codes import ErrorCode
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.redis import is_token_revoked
from app.core.security import decode_token
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

http_bearer = HTTPBearer(description="JWT Bearer token", auto_error=False)


async def get_token_from_bearer(credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer)) -> str:
    if credentials is None:
        raise UnauthorizedException(
            message="Authorization header missing",
            code=ErrorCode.UNAUTHORIZED,
        )
    return credentials.credentials


async def get_refresh_token_from_cookie(refresh_token: str | None = Cookie(None)) -> str:
    if not refresh_token:
        raise UnauthorizedException(
            message="Refresh token not found in cookie",
            code=ErrorCode.INVALID_TOKEN,
        )
    return refresh_token


async def get_current_user(
    token: str = Depends(get_token_from_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException(
            message="Invalid or malformed token",
            code=ErrorCode.INVALID_TOKEN,
        )

    if payload.get("type") != "access":
        raise UnauthorizedException(
            message="Invalid token type",
            code=ErrorCode.INVALID_TOKEN,
        )

    if await is_token_revoked(token):
        raise UnauthorizedException(
            message="Token has been revoked",
            code=ErrorCode.TOKEN_REVOKED,
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise UnauthorizedException(
            message="Invalid token payload",
            code=ErrorCode.INVALID_TOKEN,
        )

    repo = UserRepository(session)
    user = await repo.get_by_id(int(user_id_str))
    if not user:
        raise UnauthorizedException(
            message="User not found",
            code=ErrorCode.USER_NOT_FOUND,
        )
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise ForbiddenException(
            message="User account is inactive",
            code=ErrorCode.USER_INACTIVE,
        )
    return user


async def require_admin(user: User = Depends(get_current_active_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise ForbiddenException(
            message="Insufficient permissions for this action",
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        )
    return user
