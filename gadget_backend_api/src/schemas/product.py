from decimal import Decimal
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., ge=0, description="Product price")
    stock: int = Field(..., ge=0, description="Inventory stock")
    is_active: bool = Field(default=True, description="Active status")
    image_url: str | None = Field(default=None, description="Product image URL")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    price: Decimal | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = Field(default=None)
    image_url: str | None = Field(default=None)


class ProductRead(ProductBase):
    id: int = Field(..., description="Product ID")

    class Config:
        from_attributes = True
