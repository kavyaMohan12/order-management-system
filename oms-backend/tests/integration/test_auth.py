def test_register_and_login(client):
    r = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "longpassword1"},
    )
    assert r.status_code == 201
    assert r.json()["user"]["email"] == "new@example.com"
    assert "password" not in r.json()["user"]

    login = client.post(
        "/auth/login",
        json={"email": "new@example.com", "password": "longpassword1"},
    )
    assert login.status_code == 200
    body = login.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert len(body["access_token"]) > 20


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "longpassword1"}
    assert client.post("/auth/register", json=payload).status_code == 201
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "email_taken"


def test_login_invalid_credentials(client):
    client.post(
        "/auth/register",
        json={"email": "x@example.com", "password": "longpassword1"},
    )
    r = client.post(
        "/auth/login",
        json={"email": "x@example.com", "password": "wrongpassword"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth_failed"


def test_orders_require_auth(client):
    r = client.get("/orders")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth_failed"
