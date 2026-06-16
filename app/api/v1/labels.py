from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.project import get_project_in_workspace_member
from app.schemas.common import PaginatedResponse
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services.label_service import LabelService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/labels", tags=["Labels"])


@router.post("", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    workspace_id: int,
    project_id: int,
    data: LabelCreate,
    project=Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> LabelResponse:
    return await LabelService(session).create(project_id, data)


@router.patch("/{label_id}", response_model=LabelResponse)
async def update_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    data: LabelUpdate,
    project=Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> LabelResponse:
    return await LabelService(session).update(project_id, label_id, data)


@router.get("/{label_id}", response_model=LabelResponse)
async def get_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    project=Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> LabelResponse:
    return await LabelService(session).get(project_id, label_id)


@router.get("", response_model=PaginatedResponse[LabelResponse])
async def list_labels(
    workspace_id: int,
    project_id: int,
    offset: int = 0,
    limit: int = 20,
    project=Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LabelResponse]:
    return await LabelService(session).list(
        project_id, offset=offset, limit=limit
    )


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    project=Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> None:
    await LabelService(session).delete(project_id, label_id)
