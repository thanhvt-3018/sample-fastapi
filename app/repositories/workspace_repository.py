from __future__ import annotations

from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    model = Workspace


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    model = WorkspaceMember
