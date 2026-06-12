from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCode
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import ChangePasswordRequest, UserResponse, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def get_profile(self, user_id: int) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                message="User not found",
                code=ErrorCode.USER_NOT_FOUND,
            )
        return UserResponse.model_validate(user)

    async def update_profile(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                message="User not found",
                code=ErrorCode.USER_NOT_FOUND,
            )
        updated = await self._repo.update(user, **data.model_dump(exclude_unset=True))
        return UserResponse.model_validate(updated)

    async def change_password(self, user_id: int, data: ChangePasswordRequest) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                message="User not found",
                code=ErrorCode.USER_NOT_FOUND,
            )
        if not verify_password(data.current_password, user.hashed_password):
            raise UnauthorizedException(
                message="Current password is incorrect",
                code=ErrorCode.INVALID_PASSWORD,
            )
        await self._repo.update(user, hashed_password=hash_password(data.new_password))
        logger.info("Password changed for user id=%s", user_id)
