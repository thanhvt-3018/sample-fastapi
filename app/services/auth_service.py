from __future__ import annotations

import logging
from datetime import timedelta

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.enums import UserRole
from app.core.error_codes import ErrorCode
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)
from app.core.redis import is_token_revoked, revoke_token
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, data: RegisterRequest) -> dict[str, str]:
        if await self._repo.get_by_email(data.email):
            raise ConflictException(
                message="Email already registered",
                code=ErrorCode.USER_ALREADY_EXISTS,
            )

        user = await self._repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=UserRole.MEMBER,
            is_active=True,
        )
        logger.info("New user registered: id=%s email=%s", user.id, user.email)

        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
        }

    async def login(self, data: LoginRequest) -> dict[str, str]:
        user = await self._repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException(
                message="Invalid email or password",
                code=ErrorCode.INVALID_CREDENTIALS,
            )
        if not user.is_active:
            raise ForbiddenException(
                message="User account is inactive",
                code=ErrorCode.USER_INACTIVE,
            )

        logger.info("User logged in: id=%s", user.id)
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
        }

    async def refresh(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise UnauthorizedException(
                message="Invalid or expired token",
                code=ErrorCode.INVALID_TOKEN,
            )

        if payload.get("type") != "refresh":
            raise UnauthorizedException(
                message="Invalid token type",
                code=ErrorCode.INVALID_TOKEN,
            )

        if await is_token_revoked(refresh_token):
            raise UnauthorizedException(
                message="Token has been revoked",
                code=ErrorCode.TOKEN_REVOKED,
            )

        user_id = int(payload["sub"])
        user = await self._repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException(
                message="User not found or inactive",
                code=ErrorCode.USER_NOT_FOUND,
            )

        # Revoke old refresh token
        await revoke_token(
            refresh_token,
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
        }

    async def logout(self, user_id: int, access_token: str, refresh_token: str) -> None:
        await revoke_token(
            access_token,
            timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        await revoke_token(
            refresh_token,
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        logger.info("User logged out: id=%s", user_id)
