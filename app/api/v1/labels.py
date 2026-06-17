from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceMemberRole
from app.core.permission_decorator import workspace_permission
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.dependencies.project import get_project
from app.dependencies.label import find_label
from app.models.label import Label
from app.models.project import Project
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services.label_service import LabelService

router = APIRouter(
    prefix="/projects/{project_id}/labels", tags=["Labels"])


@router.post("", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def create_label(
    workspace_id: int,
    project_id: int,
    data: LabelCreate,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
) -> LabelResponse:
    return await LabelService(session).create(project_id, data)


@router.patch("/{label_id}", response_model=LabelResponse)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def update_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    data: LabelUpdate,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    label: Label = Depends(find_label),
    session: AsyncSession = Depends(get_db),
) -> LabelResponse:
    return await LabelService(session).update(label, data)


@router.get("/{label_id}", response_model=LabelResponse)
@workspace_permission([WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def get_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    label: Label = Depends(find_label),
    session: AsyncSession = Depends(get_db),
) -> LabelResponse:
    return await LabelService(session).get(label)


@router.get("", response_model=PaginatedResponse[LabelResponse])
@workspace_permission([WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def list_labels(
    workspace_id: int,
    project_id: int,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LabelResponse]:
    return await LabelService(session).list(
        project_id, page=page, limit=limit
    )


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def delete_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    label: Label = Depends(find_label),
    session: AsyncSession = Depends(get_db),
) -> None:
    await LabelService(session).delete(label)
