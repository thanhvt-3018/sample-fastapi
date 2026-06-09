from typing import Optional
from app.schemas.item import ItemCreate, ItemUpdate


class ItemModel:
    def __init__(self, id: int, name: str, description: Optional[str], price: float, is_available: bool):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.is_available = is_available


class ItemRepository:
    def __init__(self) -> None:
        self._store: dict[int, ItemModel] = {}
        self._next_id: int = 1

    def get_all(self) -> list[ItemModel]:
        return list(self._store.values())

    def get_by_id(self, item_id: int) -> Optional[ItemModel]:
        return self._store.get(item_id)

    def create(self, data: ItemCreate) -> ItemModel:
        item = ItemModel(
            id=self._next_id,
            name=data.name,
            description=data.description,
            price=data.price,
            is_available=data.is_available,
        )
        self._store[self._next_id] = item
        self._next_id += 1
        return item

    def update(self, item_id: int, data: ItemUpdate) -> Optional[ItemModel]:
        item = self._store.get(item_id)
        if item is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        return item

    def delete(self, item_id: int) -> bool:
        if item_id not in self._store:
            return False
        del self._store[item_id]
        return True
