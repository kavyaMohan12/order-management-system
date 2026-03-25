def test_list_products_public(client):
    r = client.get("/products")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert {p["name"] for p in data} == {"Test Alpha", "Test Beta"}
