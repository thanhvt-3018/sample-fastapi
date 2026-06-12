from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.project import get_project_in_workspace_member
from app.dependencies.workspace import get_workspace_member
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: int,
    data: ProjectCreate,
    workspace=Depends(get_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    return await ProjectService(session).create(workspace_id, data)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_endpoint(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    return await ProjectService(session).get(project)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    workspace_id: int,
    offset: int = 0,
    limit: int = 20,
    workspace=Depends(get_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    projects, _ = await ProjectService(session).list(
        workspace_id, offset=offset, limit=limit
    )
    return projects


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    workspace_id: int,
    project_id: int,
    data: ProjectUpdate,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    return await ProjectService(session).update(project, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> None:
    await ProjectService(session).delete(project)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    return await ProjectService(session).archive(project)


@router.post("/{project_id}/unarchive", response_model=ProjectResponse)
async def unarchive_project(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    return await ProjectService(session).unarchive(project)
