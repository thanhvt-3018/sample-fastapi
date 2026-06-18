from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permission_decorator import workspace_permission
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.dependencies.project import get_project
from app.dependencies.task import get_task
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.core.enums import TaskStatus, TaskPriority, WorkspaceMemberRole
from app.core.redis import get_redis, get_task_cache_key, invalidate_project_task_cache
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/tasks", tags=["Tasks"]
)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def create_task(
    workspace_id: int,
    project_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    result = await TaskService(session).create(project_id, current_user.id, data)
    await invalidate_project_task_cache(project_id)
    return result


@router.get("/{task_id}", response_model=TaskResponse)
@workspace_permission(
    [WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER]
)
async def get_task_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(session).get(task)


@router.get("", response_model=PaginatedResponse[TaskResponse])
@workspace_permission(
    [WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER]
)
async def list_tasks(
    workspace_id: int,
    project_id: int,
    page: int = 1,
    limit: int = 20,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TaskResponse]:
    cache_key = get_task_cache_key(
        project_id, page, limit, status, priority, assignee_id
    )
    redis = get_redis()

    cached = await redis.get(cache_key)
    if cached:
        return PaginatedResponse.model_validate_json(cached)

    result = await TaskService(session).list(
        project_id,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
    )

    await redis.setex(cache_key, 3600, result.model_dump_json())
    return result


@router.patch("/{task_id}", response_model=TaskResponse)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def update_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    result = await TaskService(session).update(task, data)
    await invalidate_project_task_cache(project_id)
    return result


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def delete_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task),
    session: AsyncSession = Depends(get_db),
) -> None:
    await TaskService(session).delete(task)
    await invalidate_project_task_cache(project_id)


@router.post("/{task_id}/labels/{label_id}", response_model=TaskResponse)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def add_label_to_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    label_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    result = await TaskService(session).add_label(task, label_id)
    await invalidate_project_task_cache(project_id)
    return result


@router.delete("/{task_id}/labels/{label_id}", response_model=TaskResponse)
@workspace_permission([WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER])
async def remove_label_from_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    label_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    result = await TaskService(session).remove_label(task, label_id)
    await invalidate_project_task_cache(project_id)
    return result


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
@workspace_permission(
    [WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER]
)
async def add_comment_to_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    data: CommentCreate,
    task: Task = Depends(get_task),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> CommentResponse:
    return await TaskService(session).add_comment(task, current_user.id, data)


@router.delete(
    "/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
@workspace_permission(
    [WorkspaceMemberRole.VIEWER, WorkspaceMemberRole.EDITOR, WorkspaceMemberRole.OWNER]
)
async def remove_comment_from_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task),
    session: AsyncSession = Depends(get_db),
) -> None:
    await TaskService(session).remove_comment(task, comment_id)
