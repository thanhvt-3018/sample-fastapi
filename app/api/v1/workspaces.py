from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole, WorkspaceMemberRole
from app.core.permission_decorator import user_permission, workspace_permission
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.dependencies.workspace import find_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.common import PaginatedResponse
from app.schemas.workspace import (
    InviteMemberRequest,
    UpdateMemberRoleRequest,
    WorkspaceMemberResponse,
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
@user_permission([UserRole.ADMIN])
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    return await WorkspaceService(session).create(current_user.id, data)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
@workspace_permission([WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def get_workspace_details(
    workspace_id: int,
    workspace: Workspace = Depends(find_workspace),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=PaginatedResponse[WorkspaceResponse])
async def list_workspaces(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkspaceResponse]:
    return await WorkspaceService(session).list(
        current_user.id, page=page, limit=limit
    )


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def update_workspace(
    workspace_id: int,
    data: WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user),
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    return await WorkspaceService(session).update(workspace, data)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def delete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_active_user),
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
) -> None:
    await WorkspaceService(session).delete(workspace)


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=status.HTTP_201_CREATED)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def invite_member(
    workspace_id: int,
    data: InviteMemberRequest,
    current_user: User = Depends(get_current_active_user),
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceMemberResponse:
    return await WorkspaceService(session).invite_member(workspace, data)


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def remove_member(
    workspace_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
) -> None:
    await WorkspaceService(session).remove_member(workspace, user_id)


@router.put("/{workspace_id}/members/{user_id}/role", response_model=WorkspaceMemberResponse)
@workspace_permission([WorkspaceMemberRole.OWNER])
async def update_member_role(
    workspace_id: int,
    user_id: int,
    data: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_active_user),
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceMemberResponse:
    return await WorkspaceService(session).update_member_role(workspace, user_id, data.role)


@router.get("/{workspace_id}/members", response_model=PaginatedResponse[WorkspaceMemberResponse])
@workspace_permission([WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def list_members(
    workspace_id: int,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    workspace: Workspace = Depends(find_workspace),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkspaceMemberResponse]:
    return await WorkspaceService(session).get_members(
        workspace, page=page, limit=limit
    )
