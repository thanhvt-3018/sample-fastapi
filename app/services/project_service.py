from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ProjectStatus
from app.models.project import Project
from app.repositories.label_repository import LabelRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.common import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._project_repo = ProjectRepository(session)
        self._workspace_repo = WorkspaceRepository(session)
        self._task_repo = TaskRepository(session)
        self._label_repo = LabelRepository(session)
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

    async def list(self, workspace_id: int, *, page: int = 1, limit: int = 20) -> PaginatedResponse:
        result = await self._project_repo.paginate(
            page=page,
            limit=limit,
            workspace_id=workspace_id,
        )
        return PaginatedResponse(
            items=[ProjectResponse.model_validate(p) for p in result.items],
            total=result.total,
            page=result.page,
            limit=result.limit,
        )

    async def update(self, project: Project, data: ProjectUpdate) -> ProjectResponse:
        updated = await self._project_repo.update(
            project,
            **data.model_dump(exclude_unset=True),
        )
        return ProjectResponse.model_validate(updated)

    async def delete(self, project: Project) -> None:
        await self._project_repo.delete(project)
        await self.session.commit()

    async def archive(self, project: Project) -> ProjectResponse:
        updated = await self._project_repo.update(project, status=ProjectStatus.ARCHIVED)
        return ProjectResponse.model_validate(updated)

    async def unarchive(self, project: Project) -> ProjectResponse:
        updated = await self._project_repo.update(project, status=ProjectStatus.ACTIVE)
        return ProjectResponse.model_validate(updated)
