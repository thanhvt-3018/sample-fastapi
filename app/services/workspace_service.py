from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceMemberRole
from app.core.error_codes import ErrorCode
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import (
    WorkspaceRepository,
    WorkspaceMemberRepository,
)
from app.schemas.workspace import (
    InviteMemberRequest,
    WorkspaceMemberResponse,
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self._workspace_repo = WorkspaceRepository(session)
        self._member_repo = WorkspaceMemberRepository(session)
        self._user_repo = UserRepository(session)
        self.session = session

    async def create(self, user_id: int, data: WorkspaceCreate) -> WorkspaceResponse:
        workspace = await self._workspace_repo.create(
            name=data.name,
            owner_id=user_id,
        )
        return WorkspaceResponse.model_validate(workspace)

    async def get(self, workspace_id: int) -> WorkspaceResponse:
        workspace = await self._workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException(
                message="Workspace not found",
                code=ErrorCode.WORKSPACE_NOT_FOUND,
            )
        return WorkspaceResponse.model_validate(workspace)

    async def list(self, user_id: int, *, offset: int = 0, limit: int = 20) -> tuple[list[WorkspaceResponse], int]:
        workspaces, total = await self._workspace_repo.paginate(
            offset=offset,
            limit=limit,
            owner_id=user_id,
        )

        return (
            [WorkspaceResponse.model_validate(w) for w in workspaces],
            total,
        )

    async def update(self, workspace: Workspace, data: WorkspaceUpdate) -> WorkspaceResponse:
        updated = await self._workspace_repo.update(
            workspace,
            **data.model_dump(exclude_unset=True),
        )
        return WorkspaceResponse.model_validate(updated)

    async def delete(self, workspace: Workspace) -> None:
        await self._workspace_repo.delete(workspace)

    async def invite_member(
        self,
        workspace: Workspace,
        data: InviteMemberRequest,
    ) -> WorkspaceMemberResponse:
        target_user = await self._user_repo.get_by_id(data.user_id)
        if not target_user:
            raise NotFoundException(
                message="User not found",
                code=ErrorCode.USER_NOT_FOUND,
            )

        existing = await self.session.execute(
            select(WorkspaceMember).where(
                (WorkspaceMember.workspace_id == workspace.id)
                & (WorkspaceMember.user_id == data.user_id)
                & (WorkspaceMember.deleted_at.is_(None))
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException(
                message="User is already a member of this workspace",
                code=ErrorCode.MEMBER_ALREADY_EXISTS,
            )

        member = await self._member_repo.create(
            workspace_id=workspace.id,
            user_id=data.user_id,
            role=data.role,
        )
        return WorkspaceMemberResponse.model_validate(member)

    async def remove_member(self, workspace: Workspace, member_user_id: int) -> None:
        if workspace.owner_id == member_user_id:
            raise ForbiddenException(
                message="Cannot remove workspace owner",
                code=ErrorCode.CANNOT_REMOVE_OWNER,
            )

        member = await self.session.execute(
            select(WorkspaceMember).where(
                (WorkspaceMember.workspace_id == workspace.id)
                & (WorkspaceMember.user_id == member_user_id)
                & (WorkspaceMember.deleted_at.is_(None))
            )
        )
        member_obj = member.scalar_one_or_none()
        if not member_obj:
            raise NotFoundException(
                message="Member not found in workspace",
                code=ErrorCode.MEMBER_NOT_FOUND,
            )

        await self._member_repo.delete(member_obj)

    async def update_member_role(
        self,
        workspace: Workspace,
        member_user_id: int,
        role: WorkspaceMemberRole,
    ) -> WorkspaceMemberResponse:
        member = await self.session.execute(
            select(WorkspaceMember).where(
                (WorkspaceMember.workspace_id == workspace.id)
                & (WorkspaceMember.user_id == member_user_id)
                & (WorkspaceMember.deleted_at.is_(None))
            )
        )
        member_obj = member.scalar_one_or_none()
        if not member_obj:
            raise NotFoundException(
                message="Member not found in workspace",
                code=ErrorCode.MEMBER_NOT_FOUND,
            )

        updated = await self._member_repo.update(member_obj, role=role)
        return WorkspaceMemberResponse.model_validate(updated)

    async def get_members(self, workspace: Workspace, *, offset: int = 0, limit: int = 20) -> tuple[list[WorkspaceMemberResponse], int]:
        query = select(WorkspaceMember).where(
            (WorkspaceMember.workspace_id == workspace.id)
            & (WorkspaceMember.deleted_at.is_(None))
        )

        count_query = select(func.count()).select_from(WorkspaceMember).where(
            (WorkspaceMember.workspace_id == workspace.id)
            & (WorkspaceMember.deleted_at.is_(None))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        members = list(result.scalars().all())

        return (
            [WorkspaceMemberResponse.model_validate(m) for m in members],
            total,
        )
