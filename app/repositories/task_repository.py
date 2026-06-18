from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    model = Task

    async def create(self, **kwargs: Any) -> Task:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance, ["labels"])
        return instance

    async def get_by_id(self, id: int):
        stmt = (
            select(self.model)
            .where((self.model.id == id) & (self.model.deleted_at.is_(None)))
            .options(selectinload(self.model.labels))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_label(self, task: Task, label) -> Task:
        if label not in task.labels:
            task.labels.append(label)
            await self.session.commit()
            await self.session.refresh(task, ["labels"])
        return task

    async def remove_label(self, task: Task, label) -> Task:
        if label in task.labels:
            task.labels.remove(label)
            await self.session.commit()
            await self.session.refresh(task, ["labels"])
        return task
