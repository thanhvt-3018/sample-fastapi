from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ERROR_MESSAGES, ErrorCode
from app.core.exceptions import NotFoundException
from app.dependencies.database import get_db
from app.models.task import Task
from app.repositories.task_repository import TaskRepository


async def get_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
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

    return task
