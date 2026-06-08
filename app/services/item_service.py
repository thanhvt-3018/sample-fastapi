from fastapi import HTTPException, status

from app.repositories.item_repository import ItemRepository, ItemModel
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self._repo = repository

    def list_items(self) -> list[ItemModel]:
        return self._repo.get_all()

    def get_item(self, item_id: int) -> ItemModel:
        item = self._repo.get_by_id(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id={item_id} not found",
            )
        return item

    def create_item(self, data: ItemCreate) -> ItemModel:
        return self._repo.create(data)

    def update_item(self, item_id: int, data: ItemUpdate) -> ItemModel:
        item = self._repo.update(item_id, data)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id={item_id} not found",
            )
        return item

    def delete_item(self, item_id: int) -> None:
        deleted = self._repo.delete(item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id={item_id} not found",
            )
