from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    assignee_id: int | None = None


class TaskFilterParams(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assignee_id: int | None
    created_by: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    labels: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def extract_labels(cls, data):
        if isinstance(data, dict):
            return data

        try:
            labels_list = []
            if hasattr(data, "labels"):
                try:
                    labels_list = [label.name for label in data.labels]
                except Exception:
                    labels_list = []

            return {
                "id": data.id,
                "project_id": data.project_id,
                "assignee_id": data.assignee_id,
                "created_by": data.created_by,
                "title": data.title,
                "description": data.description,
                "status": data.status,
                "priority": data.priority,
                "due_date": data.due_date,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "labels": labels_list,
            }
        except Exception:
            return data
