from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceMemberRole
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.dependencies.workspace import get_workspace_owner, get_workspace_member
from app.models.user import User
from app.models.workspace import Workspace
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
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    return await WorkspaceService(session).create(current_user.id, data)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    workspace: Workspace = Depends(get_workspace_owner),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    offset: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> list[WorkspaceResponse]:
    workspaces, _ = await WorkspaceService(session).list(current_user.id, offset=offset, limit=limit)
    return workspaces


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    data: WorkspaceUpdate,
    workspace: Workspace = Depends(get_workspace_owner),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    return await WorkspaceService(session).update(workspace, data)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    workspace: Workspace = Depends(get_workspace_owner),
    session: AsyncSession = Depends(get_db),
) -> None:
    await WorkspaceService(session).delete(workspace)


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    workspace_id: int,
    data: InviteMemberRequest,
    workspace: Workspace = Depends(get_workspace_owner),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceMemberResponse:
    return await WorkspaceService(session).invite_member(workspace, data)


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: int,
    user_id: int,
    workspace: Workspace = Depends(get_workspace_owner),
    session: AsyncSession = Depends(get_db),
) -> None:
    await WorkspaceService(session).remove_member(workspace, user_id)


@router.put("/{workspace_id}/members/{user_id}/role", response_model=WorkspaceMemberResponse)
async def update_member_role(
    workspace_id: int,
    user_id: int,
    data: UpdateMemberRoleRequest,
    workspace: Workspace = Depends(get_workspace_owner),
    session: AsyncSession = Depends(get_db),
) -> WorkspaceMemberResponse:
    return await WorkspaceService(session).update_member_role(workspace, user_id, data.role)


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_members(
    workspace_id: int,
    offset: int = 0,
    limit: int = 20,
    workspace: Workspace = Depends(get_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> list[WorkspaceMemberResponse]:
    members, _ = await WorkspaceService(session).get_members(workspace, offset=offset, limit=limit)
    return members
