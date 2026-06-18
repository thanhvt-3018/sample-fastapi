from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TaskStatus, TaskPriority
from app.core.error_codes import ERROR_MESSAGES, ErrorCode
from app.core.exceptions import NotFoundException
from app.models.task import Task
from app.repositories.comment_repository import CommentRepository
from app.repositories.label_repository import LabelRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._task_repo = TaskRepository(session)
        self._user_repo = UserRepository(session)
        self._label_repo = LabelRepository(session)
        self._comment_repo = CommentRepository(session)
        self.session = session

    async def create(self, project_id: int, created_by: int, data: TaskCreate) -> TaskResponse:
        if data.assignee_id:
            assignee = await self._user_repo.get_by_id(data.assignee_id)
            if not assignee:
                raise NotFoundException(
                    message=ERROR_MESSAGES[ErrorCode.USER_NOT_FOUND],
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

    async def list(self, project_id: int, *, page: int = 1, limit: int = 20, status: TaskStatus | None = None, priority: TaskPriority | None = None, assignee_id: int | None = None) -> PaginatedResponse:
        result = await self._task_repo.paginate(
            page=page,
            limit=limit,
            load=["labels"],
            project_id=project_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )
        return PaginatedResponse(
            items=[TaskResponse.model_validate(t) for t in result.items],
            total=result.total,
            page=result.page,
            limit=result.limit,
        )

    async def update(self, task: Task, data: TaskUpdate) -> TaskResponse:
        update_data = data.model_dump(exclude_unset=True)

        if "assignee_id" in update_data and update_data["assignee_id"]:
            assignee = await self._user_repo.get_by_id(update_data["assignee_id"])
            if not assignee:
                raise NotFoundException(
                    message=ERROR_MESSAGES[ErrorCode.USER_NOT_FOUND],
                    code=ErrorCode.USER_NOT_FOUND,
                )

        updated = await self._task_repo.update(task, **update_data)
        return TaskResponse.model_validate(updated)

    async def delete(self, task: Task) -> None:
        await self._task_repo.delete(task)
        await self.session.commit()

    async def add_label(self, task: Task, label_id: int) -> TaskResponse:
        label = await self._label_repo.get_by_id(label_id)
        if not label:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )

        if label.project_id != task.project_id:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )

        updated = await self._task_repo.add_label(task, label)
        return TaskResponse.model_validate(updated)

    async def remove_label(self, task: Task, label_id: int) -> TaskResponse:
        label = await self._label_repo.get_by_id(label_id)
        if not label:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )

        if label.project_id != task.project_id:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )

        updated = await self._task_repo.remove_label(task, label)
        return TaskResponse.model_validate(updated)

    async def add_comment(self, task: Task, author_id: int, data: CommentCreate) -> CommentResponse:
        comment = await self._comment_repo.create(
            task_id=task.id,
            author_id=author_id,
            content=data.content,
        )
        return CommentResponse.model_validate(comment)

    async def remove_comment(self, task: Task, comment_id: int) -> None:
        comment = await self._comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.COMMENT_NOT_FOUND],
                code=ErrorCode.COMMENT_NOT_FOUND,
            )
        if comment.task_id != task.id:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.COMMENT_NOT_FOUND],
                code=ErrorCode.COMMENT_NOT_FOUND,
            )
        await self._comment_repo.delete(comment)
        await self.session.commit()
