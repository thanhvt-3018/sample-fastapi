from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Laptop"])
    description: Optional[str] = Field(
        default=None, max_length=500, examples=["A powerful laptop"])
    price: float = Field(..., gt=0, examples=[999.99])
    is_available: bool = Field(default=True)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, gt=0)
    is_available: Optional[bool] = None


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
