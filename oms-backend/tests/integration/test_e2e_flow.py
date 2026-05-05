from app.models import Product


def test_full_user_journey(client, db_session):
    register = client.post(
        "/auth/register",
        json={"email": "buyer@example.com", "password": "longpassword1"},
    )
    assert register.status_code == 201
    assert register.json()["user"]["email"] == "buyer@example.com"

    login = client.post(
        "/auth/login",
        json={"email": "buyer@example.com", "password": "longpassword1"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    products = client.get("/products")
    assert products.status_code == 200
    catalog = products.json()
    assert len(catalog) >= 2
    product_a, product_b = catalog[0], catalog[1]
    stock_a_before = db_session.get(Product, product_a["id"]).stock
    stock_b_before = db_session.get(Product, product_b["id"]).stock

    create = client.post(
        "/orders",
        headers=headers,
        json={
            "shipping_address": "1 Buyer Lane",
            "items": [
                {"product_id": product_a["id"], "quantity": 2},
                {"product_id": product_b["id"], "quantity": 1},
            ],
        },
    )
    assert create.status_code == 201
    order = create.json()
    order_id = order["id"]
    assert order["status"] == "pending"
    assert len(order["items"]) == 2

    db_session.expire_all()
    assert db_session.get(Product, product_a["id"]).stock == stock_a_before - 2
    assert db_session.get(Product, product_b["id"]).stock == stock_b_before - 1

    listed = client.get("/orders", headers=headers)
    assert listed.status_code == 200
    assert any(o["id"] == order_id for o in listed.json())

    fetched = client.get(f"/orders/{order_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["shipping_address"] == "1 Buyer Lane"

    patched = client.patch(
        f"/orders/{order_id}",
        headers=headers,
        json={"shipping_address": "2 Buyer Lane"},
    )
    assert patched.status_code == 200
    assert patched.json()["shipping_address"] == "2 Buyer Lane"

    cancelled = client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    db_session.expire_all()
    assert db_session.get(Product, product_a["id"]).stock == stock_a_before
    assert db_session.get(Product, product_b["id"]).stock == stock_b_before

    again = client.post(f"/orders/{order_id}/cancel", headers=headers)
    assert again.status_code == 200
    assert again.json()["status"] == "cancelled"
