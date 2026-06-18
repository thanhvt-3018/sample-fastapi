from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ERROR_MESSAGES, ErrorCode
from app.core.exceptions import NotFoundException
from app.dependencies.database import get_db
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository


async def get_project(
    workspace_id: int,
    project_id: int,
    session: AsyncSession = Depends(get_db),
) -> Project:
    project = await ProjectRepository(session).get_one(
        conditions={
            "id": project_id,
            "workspace_id": workspace_id,
        },
        load=["workspace", "tasks", "labels"],
    )
    if not project:
        raise NotFoundException(
            message=ERROR_MESSAGES[ErrorCode.PROJECT_NOT_FOUND],
            code=ErrorCode.PROJECT_NOT_FOUND,
        )

    return project
