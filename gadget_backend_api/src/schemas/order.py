from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., ge=1, description="Quantity")


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., description="List of items to purchase")


class OrderRead(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    items: List[OrderItemRead]

    class Config:
        from_attributes = True
