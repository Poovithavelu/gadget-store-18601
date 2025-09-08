from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import Order, OrderItem
from src.models.product import Product


def _calc_total(items: List[OrderItem]) -> Decimal:
    """Calculate total amount for a list of order items."""
    total = Decimal("0")
    for it in items:
        total += (Decimal(str(it.unit_price)) * it.quantity)
    return total


# PUBLIC_INTERFACE
async def create_order(db: AsyncSession, user_id: int, items: List[Dict[str, Any]]) -> Order:
    """
    Create an order for a user given a list of items:
    items: [{product_id: int, quantity: int}]
    Validates availability and uses current product price.
    """
    if not items:
        raise ValueError("Order must contain at least one item")

    # Load all products referenced
    product_ids = list({it["product_id"] for it in items})
    result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
    products_by_id = {p.id: p for p in result.scalars().all()}

    order_items: List[OrderItem] = []
    for it in items:
        pid = it["product_id"]
        qty = int(it.get("quantity", 1))
        if qty <= 0:
            raise ValueError("Quantity must be at least 1")
        product = products_by_id.get(pid)
        if not product:
            raise ValueError(f"Product {pid} not found")
        if not product.is_active:
            raise ValueError(f"Product {pid} is inactive")
        if product.stock is not None and product.stock < qty:
            raise ValueError(f"Insufficient stock for product {pid}")

        # create order item snapshotting unit price
        order_items.append(OrderItem(product_id=pid, quantity=qty, unit_price=product.price))

        # decrement stock
        if product.stock is not None:
            product.stock = product.stock - qty

    order = Order(user_id=user_id, status="created")
    order.items = order_items
    # compute total
    order.total_amount = _calc_total(order_items)

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


# PUBLIC_INTERFACE
async def list_orders_for_user(db: AsyncSession, user_id: int) -> List[Order]:
    """List orders for a given user ordered by creation date descending."""
    result = await db.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()))
    return result.scalars().unique().all()


# PUBLIC_INTERFACE
async def get_order(db: AsyncSession, order_id: int, user_id: int) -> Optional[Order]:
    """Get an order by ID ensuring it belongs to the provided user."""
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user_id))
    return result.scalar_one_or_none()
