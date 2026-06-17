from __future__ import annotations

from functools import wraps
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole, WorkspaceMemberRole
from app.core.error_codes import ErrorCode
from app.core.exceptions import ForbiddenException
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.repositories.workspace_repository import WorkspaceRepository


async def _get_user_workspace_role(
    workspace_id: int,
    current_user: User,
    session: AsyncSession,
) -> WorkspaceMemberRole:
    workspace = await WorkspaceRepository(session).get_by_id(workspace_id)
    if not workspace:
        raise ForbiddenException(
            message="Workspace not found",
            code=ErrorCode.WORKSPACE_NOT_FOUND,
        )

    result = await session.execute(
        select(WorkspaceMember).where(
            (WorkspaceMember.workspace_id == workspace_id)
            & (WorkspaceMember.user_id == current_user.id)
            & (WorkspaceMember.deleted_at.is_(None))
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise ForbiddenException(
            message="You are not a member of this workspace",
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        )

    return member.role


def workspace_permission(allowed_roles: list[str]):
    allowed_role_set = set(WorkspaceMemberRole[r] for r in allowed_roles)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get("current_user")
            session: AsyncSession = kwargs.get("session")
            workspace_id: int = kwargs.get("workspace_id")

            if not current_user or not session or workspace_id is None:
                raise ForbiddenException(
                    message="Missing required dependencies",
                    code=ErrorCode.INSUFFICIENT_PERMISSIONS,
                )

            if current_user.role == UserRole.ADMIN:
                return await func(*args, **kwargs)

            role = await _get_user_workspace_role(workspace_id, current_user, session)

            if role not in allowed_role_set:
                raise ForbiddenException(
                    message=f"Permission denied. Allowed roles: {', '.join(allowed_roles)}, Your role: {role}",
                    code=ErrorCode.INSUFFICIENT_PERMISSIONS,
                )
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def user_permission(allowed_roles: list[str]):
    allowed_role_set = set(UserRole[r] for r in allowed_roles)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get("current_user")

            if current_user.role not in allowed_role_set:
                raise ForbiddenException(
                    message=f"Permission denied. Allowed roles: {', '.join(allowed_roles)}, Your role: {current_user.role}",
                    code=ErrorCode.INSUFFICIENT_PERMISSIONS,
                )
            return await func(*args, **kwargs)

        return wrapper
    return decorator
