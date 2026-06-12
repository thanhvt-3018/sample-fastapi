from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCode
from app.core.exceptions import ForbiddenException, NotFoundException
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.workspace_repository import WorkspaceRepository


async def get_workspace_owner(
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Workspace:
    workspace = await WorkspaceRepository(session).get_by_id(workspace_id)
    if not workspace:
        raise NotFoundException(
            message="Workspace not found",
            code=ErrorCode.WORKSPACE_NOT_FOUND,
        )

    if workspace.owner_id != current_user.id:
        raise ForbiddenException(
            message="Only workspace owner can perform this action",
            code=ErrorCode.NOT_WORKSPACE_OWNER,
        )

    return workspace


async def get_workspace_member(
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Workspace:
    workspace = await WorkspaceRepository(session).get_by_id(workspace_id)
    if not workspace:
        raise NotFoundException(
            message="Workspace not found",
            code=ErrorCode.WORKSPACE_NOT_FOUND,
        )

    if workspace.owner_id == current_user.id:
        return workspace
    result = await session.execute(
        select(WorkspaceMember).where(
            (WorkspaceMember.workspace_id == workspace_id)
            & (WorkspaceMember.user_id == current_user.id)
            & (WorkspaceMember.deleted_at.is_(None))
        )
    )

    if not result.scalar_one_or_none():
        raise ForbiddenException(
            message="You are not a member of this workspace",
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        )

    return workspace
