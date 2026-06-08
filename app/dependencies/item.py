from functools import lru_cache
from fastapi import Depends

from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService


@lru_cache
def get_item_repository() -> ItemRepository:
    """Singleton in-memory repository (one instance per process)."""
    return ItemRepository()


def get_item_service(
    repository: ItemRepository = Depends(get_item_repository),
) -> ItemService:
    return ItemService(repository)
