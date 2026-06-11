from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ProjectStatus
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._project_repo = ProjectRepository(session)
        self._workspace_repo = WorkspaceRepository(session)
        self.session = session

    async def create(self, workspace_id: int, data: ProjectCreate) -> ProjectResponse:
        project = await self._project_repo.create(
            workspace_id=workspace_id,
            name=data.name,
            description=data.description,
            status=ProjectStatus.ACTIVE,
        )
        return ProjectResponse.model_validate(project)

    async def get(self, project: Project) -> ProjectResponse:
        return ProjectResponse.model_validate(project)

    async def list(self, workspace_id: int, *, offset: int = 0, limit: int = 20) -> tuple[list[ProjectResponse], int]:
        projects, total = await self._project_repo.paginate(
            offset=offset,
            limit=limit,
            workspace_id=workspace_id,
        )
        return (
            [ProjectResponse.model_validate(p) for p in projects],
            total,
        )

    async def update(self, project: Project, data: ProjectUpdate) -> ProjectResponse:
        updated = await self._project_repo.update(
            project,
            **data.model_dump(exclude_unset=True),
        )
        return ProjectResponse.model_validate(updated)

    async def delete(self, project: Project) -> None:
        await self._project_repo.delete(project)

    async def archive(self, project: Project) -> ProjectResponse:
        updated = await self._project_repo.update(project, status=ProjectStatus.ARCHIVED)
        return ProjectResponse.model_validate(updated)

    async def unarchive(self, project: Project) -> ProjectResponse:
        updated = await self._project_repo.update(project, status=ProjectStatus.ACTIVE)
        return ProjectResponse.model_validate(updated)
