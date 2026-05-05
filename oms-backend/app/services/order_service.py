from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.constants import (
    ORDER_CANCELLED,
    ORDER_EDITABLE_STATUSES,
    ORDER_PENDING,
)
from app.models import Order, OrderItem, Product


def _lines_from_payload(items: list) -> list[tuple[int, int]]:
    merged: dict[int, int] = {}
    for i in items:
        merged[i.product_id] = merged.get(i.product_id, 0) + i.quantity
    return list(merged.items())


def create_order(
    db: Session,
    user_id: int,
    shipping_address: str,
    items: list,
) -> Order:
    lines = _lines_from_payload(items)
    for product_id, quantity in lines:
        product = db.get(Product, product_id)
        if not product:
            raise ValueError(f"unknown_product:{product_id}")
        if product.stock < quantity:
            raise ValueError(f"insufficient_stock:{product_id}")

    order = Order(
        user_id=user_id,
        status=ORDER_PENDING,
        shipping_address=shipping_address,
    )
    db.add(order)
    db.flush()

    for product_id, quantity in lines:
        product = db.get(Product, product_id)
        assert product is not None
        unit_price = product.price
        product.stock -= quantity
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
            )
        )
    db.commit()
    return _get_order_with_items(db, order.id)


def list_orders_for_user(db: Session, user_id: int) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
    )
    return list(db.scalars(stmt).unique().all())


def get_order_by_id(db: Session, order_id: int) -> Order | None:
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    return db.scalars(stmt).first()


def _get_order_with_items(db: Session, order_id: int) -> Order:
    order = get_order_by_id(db, order_id)
    assert order is not None
    return order


def update_order(
    db: Session,
    order: Order,
    shipping_address: str | None,
    new_items: list | None,
) -> Order:
    if order.status not in ORDER_EDITABLE_STATUSES:
        raise ValueError("not_editable")

    if new_items is not None:
        lines = _lines_from_payload(new_items)
        for oi in list(order.items):
            product = db.get(Product, oi.product_id)
            if product is not None:
                product.stock += oi.quantity
            db.delete(oi)
        db.flush()

        for product_id, quantity in lines:
            product = db.get(Product, product_id)
            if not product:
                raise ValueError(f"unknown_product:{product_id}")
            if product.stock < quantity:
                raise ValueError(f"insufficient_stock:{product_id}")

        for product_id, quantity in lines:
            product = db.get(Product, product_id)
            assert product is not None
            product.stock -= quantity
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price,
                )
            )

    if shipping_address is not None:
        order.shipping_address = shipping_address

    db.commit()
    return _get_order_with_items(db, order.id)


def cancel_order(db: Session, order: Order) -> Order:
    if order.status == ORDER_CANCELLED:
        db.refresh(order)
        return _get_order_with_items(db, order.id)

    if order.status not in ORDER_EDITABLE_STATUSES:
        raise ValueError("not_cancellable")

    for oi in order.items:
        product = db.get(Product, oi.product_id)
        if product is not None:
            product.stock += oi.quantity

    order.status = ORDER_CANCELLED
    db.commit()
    return _get_order_with_items(db, order.id)
