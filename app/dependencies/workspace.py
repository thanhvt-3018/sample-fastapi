from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCode
from app.core.exceptions import NotFoundException
from app.dependencies.database import get_db
from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository


async def find_workspace(
    workspace_id: int,
    session: AsyncSession = Depends(get_db),
) -> Workspace:
    workspace = await WorkspaceRepository(session).get_one(
        conditions={"id": workspace_id}, load=["projects", "members"]
    )
    if not workspace:
        raise NotFoundException(
            message="Workspace not found",
            code=ErrorCode.WORKSPACE_NOT_FOUND,
        )

    return workspace
