from fastapi import APIRouter, Depends, status

from app.dependencies.item import get_item_service
from app.schemas.item import ItemCreate, ItemListResponse, ItemResponse, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("", response_model=ItemListResponse, summary="List all items")
def list_items(service: ItemService = Depends(get_item_service)) -> ItemListResponse:
    items = service.list_items()
    return ItemListResponse(items=items, total=len(items))


@router.get("/{item_id}", response_model=ItemResponse, summary="Get a single item")
def get_item(item_id: int, service: ItemService = Depends(get_item_service)) -> ItemResponse:
    return service.get_item(item_id)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create a new item")
def create_item(payload: ItemCreate, service: ItemService = Depends(get_item_service)) -> ItemResponse:
    return service.create_item(payload)


@router.patch("/{item_id}", response_model=ItemResponse, summary="Partially update an item")
def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    return service.update_item(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item")
def delete_item(item_id: int, service: ItemService = Depends(get_item_service)) -> None:
    service.delete_item(item_id)
