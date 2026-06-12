from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCode
from app.core.exceptions import ForbiddenException, NotFoundException
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.project import Project
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.repositories.project_repository import ProjectRepository


async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
) -> Project:
    project = await ProjectRepository(session).get_by_id(project_id)
    if not project:
        raise NotFoundException(
            message="Project not found",
            code=ErrorCode.PROJECT_NOT_FOUND,
        )
    return project


async def get_project_in_workspace_member(
    workspace_id: int,
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Project:
    project = await ProjectRepository(session).get_by_id(project_id)
    if not project or project.workspace_id != workspace_id:
        raise NotFoundException(
            message="Project not found",
            code=ErrorCode.PROJECT_NOT_FOUND,
        )

    workspace = project.workspace

    if workspace.owner_id == current_user.id:
        return project
    result = await session.execute(
        select(WorkspaceMember).where(
            (WorkspaceMember.workspace_id == workspace.id)
            & (WorkspaceMember.user_id == current_user.id)
            & (WorkspaceMember.deleted_at.is_(None))
        )
    )

    if not result.scalar_one_or_none():
        raise ForbiddenException(
            message="You are not a member of this workspace",
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        )

    return project
