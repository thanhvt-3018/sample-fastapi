from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    model = Comment

    async def get_by_id(self, id: int):
        stmt = (
            select(self.model)
            .where((self.model.id == id) & (self.model.deleted_at.is_(None)))
            .options(selectinload(self.model.author), selectinload(self.model.task))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
