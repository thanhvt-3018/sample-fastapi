from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ERROR_MESSAGES, ErrorCode
from app.core.exceptions import ForbiddenException, NotFoundException
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository


async def get_task_in_workspace_member(
    workspace_id: int,
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Task:
    task = await TaskRepository(session).get_one(
        conditions={
            "id": task_id,
            "project_id": project_id,
        },
        load=["project", "labels", "comments"]
    )
    if not task or task.project.workspace_id != workspace_id:
        raise NotFoundException(
            message=ERROR_MESSAGES[ErrorCode.TASK_NOT_FOUND],
            code=ErrorCode.TASK_NOT_FOUND,
        )

    workspace = await session.get(Workspace, task.project.workspace_id)
    if not workspace:
        raise NotFoundException(
            message=ERROR_MESSAGES[ErrorCode.WORKSPACE_NOT_FOUND],
            code=ErrorCode.WORKSPACE_NOT_FOUND,
        )

    if workspace.owner_id == current_user.id:
        return task

    result = await session.execute(
        select(WorkspaceMember).where(
            (WorkspaceMember.workspace_id == workspace.id)
            & (WorkspaceMember.user_id == current_user.id)
            & (WorkspaceMember.deleted_at.is_(None))
        )
    )

    if not result.scalar_one_or_none():
        raise ForbiddenException(
            message=ERROR_MESSAGES[ErrorCode.INSUFFICIENT_PERMISSIONS],
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        )

    return task
