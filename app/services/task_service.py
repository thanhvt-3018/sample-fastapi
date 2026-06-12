from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCode
from app.core.exceptions import NotFoundException
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._task_repo = TaskRepository(session)
        self._user_repo = UserRepository(session)
        self.session = session

    async def create(self, project_id: int, created_by: int, data: TaskCreate) -> TaskResponse:
        if data.assignee_id:
            assignee = await self._user_repo.get_by_id(data.assignee_id)
            if not assignee:
                raise NotFoundException(
                    message="Assignee not found",
                    code=ErrorCode.USER_NOT_FOUND,
                )

        task = await self._task_repo.create(
            project_id=project_id,
            created_by=created_by,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            assignee_id=data.assignee_id,
        )
        return TaskResponse.model_validate(task)

    async def get(self, task: Task) -> TaskResponse:
        return TaskResponse.model_validate(task)

    async def list(self, project_id: int, *, offset: int = 0, limit: int = 20) -> tuple[list[TaskResponse], int]:
        tasks, total = await self._task_repo.paginate(
            offset=offset,
            limit=limit,
            project_id=project_id,
        )
        return (
            [TaskResponse.model_validate(t) for t in tasks],
            total,
        )

    async def update(self, task: Task, data: TaskUpdate) -> TaskResponse:
        update_data = data.model_dump(exclude_unset=True)

        if "assignee_id" in update_data and update_data["assignee_id"]:
            assignee = await self._user_repo.get_by_id(update_data["assignee_id"])
            if not assignee:
                raise NotFoundException(
                    message="Assignee not found",
                    code=ErrorCode.USER_NOT_FOUND,
                )

        updated = await self._task_repo.update(task, **update_data)
        return TaskResponse.model_validate(updated)

    async def delete(self, task: Task) -> None:
        await self._task_repo.delete(task)
