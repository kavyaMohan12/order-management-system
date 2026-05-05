def test_create_order_and_list(client, auth_headers):
    create = client.post(
        "/orders",
        headers=auth_headers,
        json={
            "shipping_address": "1 Test St",
            "items": [{"product_id": 1, "quantity": 2}],
        },
    )
    assert create.status_code == 201
    order = create.json()
    assert order["status"] == "pending"
    assert order["shipping_address"] == "1 Test St"
    assert len(order["items"]) == 1
    assert order["items"][0]["product_id"] == 1
    assert order["items"][0]["quantity"] == 2

    listed = client.get("/orders", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_create_order_unknown_product(client, auth_headers):
    r = client.post(
        "/orders",
        headers=auth_headers,
        json={
            "shipping_address": "1 Test St",
            "items": [{"product_id": 999, "quantity": 1}],
        },
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "unknown_product"


def test_get_order_forbidden_other_user(client, db_session, auth_headers):
    order = client.post(
        "/orders",
        headers=auth_headers,
        json={
            "shipping_address": "1 Test St",
            "items": [{"product_id": 1, "quantity": 1}],
        },
    ).json()

    client.post(
        "/auth/register",
        json={"email": "other@example.com", "password": "otherpass12"},
    )
    other_login = client.post(
        "/auth/login",
        json={"email": "other@example.com", "password": "otherpass12"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    r = client.get(f"/orders/{order['id']}", headers=other_headers)
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "forbidden"


def test_get_order_not_found(client, auth_headers):
    r = client.get("/orders/99999", headers=auth_headers)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "order_not_found"


def test_patch_order_shipping(client, auth_headers):
    order = client.post(
        "/orders",
        headers=auth_headers,
        json={
            "shipping_address": "Old Addr",
            "items": [{"product_id": 1, "quantity": 1}],
        },
    ).json()

    r = client.patch(
        f"/orders/{order['id']}",
        headers=auth_headers,
        json={"shipping_address": "New Addr"},
    )
    assert r.status_code == 200
    assert r.json()["shipping_address"] == "New Addr"


def test_cancel_order(client, auth_headers):
    order = client.post(
        "/orders",
        headers=auth_headers,
        json={
            "shipping_address": "Addr",
            "items": [{"product_id": 2, "quantity": 2}],
        },
    ).json()

    r = client.post(f"/orders/{order['id']}/cancel", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"

    again = client.post(f"/orders/{order['id']}/cancel", headers=auth_headers)
    assert again.status_code == 200
    assert again.json()["status"] == "cancelled"


def test_invalid_token_returns_401(client):
    r = client.get(
        "/orders",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth_failed"


def test_create_order_invalid_payload_returns_422(client, auth_headers):
    r = client.post(
        "/orders",
        headers=auth_headers,
        json={"shipping_address": "", "items": []},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
