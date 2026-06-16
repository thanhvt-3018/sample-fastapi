from __future__ import annotations

from sqlalchemy import select

from app.models.label import Label
from app.repositories.base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    model = Label
