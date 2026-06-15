from __future__ import annotations

from sqlalchemy import select

from app.models.label import Label
from app.repositories.base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    model = Label

    async def get_by_id_and_project(self, label_id: int, project_id: int):
        stmt = select(self.model).where(
            (self.model.id == label_id)
            & (self.model.project_id == project_id)
            & (self.model.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
