from __future__ import annotations

from app.models.label import Label
from app.repositories.label_repository import LabelRepository
from app.schemas.common import PaginatedResponse
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate


class LabelService:
    def __init__(self, session):
        self._label_repo = LabelRepository(session)
        self.session = session

    async def create(self, project_id: int, data: LabelCreate) -> LabelResponse:
        label = await self._label_repo.create(
            project_id=project_id,
            name=data.name,
            color=data.color,
        )
        return LabelResponse.model_validate(label)

    async def update(self, label: Label, data: LabelUpdate) -> LabelResponse:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self._label_repo.update(label, **update_data)
        return LabelResponse.model_validate(updated)

    async def get(self, label: Label) -> LabelResponse:
        return LabelResponse.model_validate(label)

    async def delete(self, label: Label) -> None:
        await self._label_repo.delete(label)
        await self.session.commit()

    async def list(
        self, project_id: int, *, page: int = 1, limit: int = 20
    ) -> PaginatedResponse:
        result = await self._label_repo.paginate(
            page=page, limit=limit, project_id=project_id
        )
        return PaginatedResponse(
            items=[LabelResponse.model_validate(label) for label in result.items],
            total=result.total,
            page=result.page,
            limit=result.limit,
        )
