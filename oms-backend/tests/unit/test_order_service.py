from dataclasses import dataclass

import pytest

from app.core.constants import ORDER_CANCELLED
from app.core.exceptions import (
    InsufficientStockError,
    OrderNotEditableError,
    UnknownProductError,
)
from app.models import Product
from app.services import order_service


@dataclass
class Line:
    product_id: int
    quantity: int


def test_lines_from_payload_merges_duplicates():
    lines = order_service._lines_from_payload(
        [Line(1, 2), Line(2, 3), Line(1, 5)]
    )
    assert sorted(lines) == [(1, 7), (2, 3)]


def test_create_order_decrements_stock(db_session):
    before = db_session.get(Product, 1).stock
    order = order_service.create_order(
        db_session,
        user_id=_seed_user(db_session),
        shipping_address="addr",
        items=[Line(1, 3)],
    )
    after = db_session.get(Product, 1).stock
    assert after == before - 3
    assert len(order.items) == 1
    assert order.items[0].quantity == 3


def test_create_order_unknown_product(db_session):
    with pytest.raises(UnknownProductError):
        order_service.create_order(
            db_session,
            user_id=_seed_user(db_session),
            shipping_address="addr",
            items=[Line(9999, 1)],
        )


def test_create_order_insufficient_stock(db_session):
    product = db_session.get(Product, 2)
    with pytest.raises(InsufficientStockError):
        order_service.create_order(
            db_session,
            user_id=_seed_user(db_session),
            shipping_address="addr",
            items=[Line(2, product.stock + 1)],
        )


def test_cancel_order_restores_stock(db_session):
    user_id = _seed_user(db_session)
    before = db_session.get(Product, 1).stock
    order = order_service.create_order(
        db_session, user_id, "addr", [Line(1, 4)]
    )
    assert db_session.get(Product, 1).stock == before - 4

    cancelled = order_service.cancel_order(db_session, order)
    assert cancelled.status == ORDER_CANCELLED
    assert db_session.get(Product, 1).stock == before


def test_update_order_rejects_cancelled(db_session):
    user_id = _seed_user(db_session)
    order = order_service.create_order(
        db_session, user_id, "addr", [Line(1, 1)]
    )
    order_service.cancel_order(db_session, order)

    with pytest.raises(OrderNotEditableError):
        order_service.update_order(
            db_session, order, shipping_address="new", new_items=None
        )


def _seed_user(db_session) -> int:
    from app.services import auth_service

    user = auth_service.create_user(db_session, "buyer@example.com", "longpassword1")
    return user.id
