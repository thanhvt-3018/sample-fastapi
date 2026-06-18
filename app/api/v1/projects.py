from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceMemberRole
from app.core.permission_decorator import workspace_permission
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.dependencies.project import get_project
from app.dependencies.workspace import find_workspace
from app.models.project import Project
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.common import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def create_project(
    workspace_id: int,
    data: ProjectCreate,
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    return await ProjectService(session).create(workspace_id, data)


@router.get("/{project_id}", response_model=ProjectResponse)
@workspace_permission(
    [WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER]
)
async def get_project_endpoint(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    return await ProjectService(session).get(project)


@router.get("", response_model=PaginatedResponse[ProjectResponse])
@workspace_permission(
    [WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER]
)
async def list_projects(
    workspace_id: int,
    page: int = 1,
    limit: int = 20,
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[ProjectResponse]:
    return await ProjectService(session).list(workspace_id, page=page, limit=limit)


@router.patch("/{project_id}", response_model=ProjectResponse)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def update_project(
    workspace_id: int,
    project_id: int,
    data: ProjectUpdate,
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    return await ProjectService(session).update(project, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def delete_project(
    workspace_id: int,
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
) -> None:
    await ProjectService(session).delete(project)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def archive_project(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    return await ProjectService(session).archive(project)


@router.post("/{project_id}/unarchive", response_model=ProjectResponse)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def unarchive_project(
    workspace_id: int,
    project_id: int,
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    return await ProjectService(session).unarchive(project)
