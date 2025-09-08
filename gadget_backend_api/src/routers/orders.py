from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_active_user
from src.models.user import User
from src.schemas.order import OrderCreate, OrderRead
from src.services.order_service import create_order, list_orders_for_user, get_order

router = APIRouter(tags=["Orders"])


@router.post("", response_model=OrderRead, summary="Create order", description="Create a new order for the authenticated user.")
async def create_order_endpoint(payload: OrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create an order for current user."""
    try:
        order = await create_order(db, current_user.id, [item.model_dump() for item in payload.items])
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[OrderRead], summary="List my orders", description="List all orders for the authenticated user.")
async def list_my_orders(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """List orders for current user."""
    orders = await list_orders_for_user(db, current_user.id)
    return orders


@router.get("/{order_id}", response_model=OrderRead, summary="Get my order", description="Get a specific order by ID for the authenticated user.")
async def get_my_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a single order for current user."""
    order = await get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
