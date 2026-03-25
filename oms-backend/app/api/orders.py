from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate
from app.services import order_service

router = APIRouter()


def _map_order_error(exc: ValueError) -> HTTPException:
    msg = str(exc)
    if msg.startswith("unknown_product:"):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more product IDs are invalid",
        )
    if msg.startswith("insufficient_stock:"):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock for one or more products",
        )
    if msg == "not_editable":
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be updated in its current status",
        )
    if msg == "not_cancellable":
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled in its current status",
        )
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=msg,
    )


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return order_service.create_order(
            db,
            current_user.id,
            body.shipping_address,
            body.items,
        )
    except ValueError as e:
        raise _map_order_error(e) from e


@router.get("", response_model=list[OrderRead])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_service.list_orders_for_user(db, current_user.id)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return order


@router.patch("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    body: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return order_service.update_order(
            db,
            order,
            body.shipping_address,
            body.items,
        )
    except ValueError as e:
        raise _map_order_error(e) from e


@router.post("/{order_id}/cancel", response_model=OrderRead)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return order_service.cancel_order(db, order)
    except ValueError as e:
        raise _map_order_error(e) from e
