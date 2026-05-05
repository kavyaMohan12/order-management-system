from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.responses import ORDER_RO_ERRORS, ORDER_RW_ERRORS
from app.core.database import get_db
from app.models import User
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate
from app.services import order_service

router = APIRouter()


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order",
    description="Create a new order for the authenticated user. Validates product IDs and stock; snapshots `unit_price` per line.",
    responses=ORDER_RW_ERRORS,
)
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_service.create_order(
        db,
        current_user.id,
        body.shipping_address,
        body.items,
    )


@router.get(
    "",
    response_model=list[OrderRead],
    summary="List my orders",
    description="List orders belonging to the authenticated user, newest first.",
    responses=ORDER_RO_ERRORS,
)
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_service.list_orders_for_user(db, current_user.id)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Get one order",
    description="Get a single order by id. Returns 404 if missing, 403 if it belongs to another user.",
    responses=ORDER_RO_ERRORS,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_service.load_owned_order(db, order_id, current_user)


@router.patch(
    "/{order_id}",
    response_model=OrderRead,
    summary="Update an order",
    description="Update `shipping_address` and/or replace `items` (owner only, while status is `pending`/`confirmed`).",
    responses=ORDER_RW_ERRORS,
)
def update_order(
    order_id: int,
    body: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.load_owned_order(db, order_id, current_user)
    return order_service.update_order(
        db,
        order,
        body.shipping_address,
        body.items,
    )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderRead,
    summary="Cancel an order",
    description="Cancel an order (owner only). Restores stock. Idempotent if already cancelled.",
    responses=ORDER_RW_ERRORS,
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.load_owned_order(db, order_id, current_user)
    return order_service.cancel_order(db, order)
