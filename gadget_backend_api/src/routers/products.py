from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_admin_user
from src.schemas.product import ProductCreate, ProductRead, ProductUpdate
from src.services.product_service import list_products, get_product, create_product, update_product, delete_product

router = APIRouter(tags=["Products"])


@router.get("", response_model=List[ProductRead], summary="List products", description="List active products in the catalog.")
async def list_products_endpoint(db: AsyncSession = Depends(get_db), active_only: bool = Query(default=True, description="Only active products")):
    """List products."""
    products = await list_products(db, active_only=active_only)
    return products


@router.get("/{product_id}", response_model=ProductRead, summary="Get product", description="Get product details by ID.")
async def get_product_endpoint(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single product by ID."""
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("", response_model=ProductRead, summary="Create product", description="Admin: Create a new product.", dependencies=[Depends(get_current_admin_user)])
async def create_product_endpoint(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Create a new product (admin only)."""
    product = await create_product(db, payload.model_dump())
    return product


@router.put("/{product_id}", response_model=ProductRead, summary="Update product", description="Admin: Update an existing product.", dependencies=[Depends(get_current_admin_user)])
async def update_product_endpoint(product_id: int, payload: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """Update product (admin only)."""
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    product = await update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=204, summary="Delete product", description="Admin: Delete a product.", dependencies=[Depends(get_current_admin_user)])
async def delete_product_endpoint(product_id: int, db: AsyncSession = Depends(get_db)):
    """Delete product (admin only)."""
    ok = await delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return None
