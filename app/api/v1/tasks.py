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


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    workspace_id: int,
    project_id: int,
    offset: int = 0,
    limit: int = 20,
    project: Project = Depends(get_project_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    tasks, _ = await TaskService(session).list(
        project_id, offset=offset, limit=limit
    )
    return tasks


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
    task: Task = Depends(get_task_in_workspace_member),
    session: AsyncSession = Depends(get_db),
) -> None:
    await TaskService(session).delete(task)
