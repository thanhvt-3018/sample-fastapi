from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> ModelT | None:
        stmt = select(self.model).where(
            (self.model.id == id) & (self.model.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, **kwargs: Any) -> ModelT:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        if hasattr(instance, "deleted_at"):
            setattr(instance, "deleted_at", datetime.now())
            await self.session.flush()

    async def paginate(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        **filters: Any,
    ) -> tuple[list[ModelT], int]:
        stmt = select(self.model).where(self.model.deleted_at.is_(None))
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
        return list(rows), total
