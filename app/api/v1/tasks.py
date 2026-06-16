from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.dependencies.project import get_project_in_workspace_member
from app.dependencies.task import get_task_in_workspace_member
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    workspace_id: int,
    project_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(session).create(project_id, current_user.id, data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(session).get(task)


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    workspace_id: int,
    project_id: int,
    page: int = 1,
    limit: int = 20,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TaskResponse]:
    return await TaskService(session).list(
        project_id, page=page, limit=limit
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(session).update(task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> None:
    await TaskService(session).delete(task)


@router.post("/{task_id}/labels/{label_id}", response_model=TaskResponse)
async def add_label_to_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    label_id: int,
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(session).add_label(task, label_id)


@router.delete("/{task_id}/labels/{label_id}", response_model=TaskResponse)
async def remove_label_from_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    label_id: int,
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    return await TaskService(session).remove_label(task, label_id)


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment_to_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    data: CommentCreate,
    task: Task = Depends(get_task_in_workspace_member),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> CommentResponse:
    return await TaskService(session).add_comment(task, current_user.id, data)


@router.delete("/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_comment_from_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> None:
    await TaskService(session).remove_comment(task, comment_id)
