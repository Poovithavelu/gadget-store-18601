from typing import List, Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import Product


# PUBLIC_INTERFACE
async def list_products(db: AsyncSession, active_only: bool = True) -> List[Product]:
    """List products, optionally filtering to only active ones."""
    stmt = select(Product)
    if active_only:
        stmt = stmt.where(Product.is_active.is_(True))
    stmt = stmt.order_by(Product.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


# PUBLIC_INTERFACE
async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
    """Fetch a single product by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


# PUBLIC_INTERFACE
async def create_product(db: AsyncSession, data: Dict[str, Any]) -> Product:
    """Create a new product from provided data dict."""
    product = Product(**data)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


# PUBLIC_INTERFACE
async def update_product(db: AsyncSession, product_id: int, data: Dict[str, Any]) -> Optional[Product]:
    """Update an existing product by ID with given fields and return the updated entity."""
    # Ensure product exists
    product = await get_product(db, product_id)
    if not product:
        return None
    # Apply updates
    for k, v in data.items():
        setattr(product, k, v)
    await db.commit()
    await db.refresh(product)
    return product


# PUBLIC_INTERFACE
async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Delete a product by ID. Returns True if deleted, False if not found."""
    product = await get_product(db, product_id)
    if not product:
        return False
    await db.delete(product)
    await db.commit()
    return True
