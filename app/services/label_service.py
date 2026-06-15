from __future__ import annotations

from app.core.error_codes import ERROR_MESSAGES, ErrorCode
from app.core.exceptions import NotFoundException
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

    async def update(self, project_id: int, label_id: int, data: LabelUpdate) -> LabelResponse:
        label = await self._label_repo.get_by_id_and_project(label_id, project_id)
        if not label:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self._label_repo.update(label, **update_data)
        return LabelResponse.model_validate(updated)

    async def get(self, project_id: int, label_id: int) -> LabelResponse:
        label = await self._label_repo.get_by_id_and_project(label_id, project_id)
        if not label:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )
        return LabelResponse.model_validate(label)

    async def delete(self, project_id: int, label_id: int) -> None:
        label = await self._label_repo.get_by_id_and_project(label_id, project_id)
        if not label:
            raise NotFoundException(
                message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
                code=ErrorCode.LABEL_NOT_FOUND,
            )
        await self._label_repo.delete(label)

    async def list(self, project_id: int, *, offset: int = 0, limit: int = 20) -> PaginatedResponse:
        result = await self._label_repo.paginate(offset=offset, limit=limit, project_id=project_id)
        return PaginatedResponse(
            items=[LabelResponse.model_validate(l) for l in result.items],
            total=result.total,
            page=result.page,
            limit=result.limit,
        )
