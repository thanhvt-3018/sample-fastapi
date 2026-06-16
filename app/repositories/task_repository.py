from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.repositories.base import BaseRepository
from app.schemas.common import PaginatedResponse


class TaskRepository(BaseRepository[Task]):
    model = Task

    async def create(self, **kwargs: Any) -> Task:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance, ["labels"])
        return instance

    # async def update(self, instance: Task, **kwargs: Any) -> Task:
    #     for key, value in kwargs.items():
    #         setattr(instance, key, value)
    #     await self.session.flush()
    #     await self.session.refresh(instance, ["labels"])
    #     return instance

    async def get_by_id(self, id: int):
        stmt = select(self.model).where(
            (self.model.id == id) & (self.model.deleted_at.is_(None))
        ).options(selectinload(self.model.labels))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def paginate(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        **filters: Any,
    ) -> PaginatedResponse:
        stmt = select(self.model).where(self.model.deleted_at.is_(None)).options(
            selectinload(self.model.labels)
        )
        count_stmt = select(func.count()).select_from(self.model).where(
            self.model.deleted_at.is_(None)
        )

        for attr, value in filters.items():
            if value is None:
                continue
            col = getattr(self.model, attr, None)
            if col is None:
                raise ValueError(
                    f"Invalid filter field '{attr}' for {self.model.__name__}")
            stmt = stmt.where(col == value)
            count_stmt = count_stmt.where(col == value)

        total = (await self.session.execute(count_stmt)).scalar_one()
        rows = (await self.session.execute(stmt.offset(offset).limit(limit))).scalars().all()

        page = offset // limit + 1 if limit > 0 else 1
        return PaginatedResponse(items=list(rows), total=total, page=page, limit=limit)

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
