from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ERROR_MESSAGES, ErrorCode
from app.core.exceptions import NotFoundException
from app.dependencies.database import get_db
from app.models.label import Label
from app.repositories.label_repository import LabelRepository


async def find_label(
    project_id: int,
    label_id: int,
    session: AsyncSession = Depends(get_db),
) -> Label:
    label = await LabelRepository(session).get_one(
        conditions={
            "id": label_id,
            "project_id": project_id,
        }
    )
    if not label:
        raise NotFoundException(
            message=ERROR_MESSAGES[ErrorCode.LABEL_NOT_FOUND],
            code=ErrorCode.LABEL_NOT_FOUND,
        )
    return label
