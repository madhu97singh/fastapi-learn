from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_item():
    response = client.post("/items", json={"name": "Laptop", "price": 999.99})
    assert response.status_code == 201
    assert response.json()["name"] == "Laptop"


def test_create_then_read_item():
    created = client.post("/items", json={"name": "Mouse", "price": 25.0})
    item_id = created.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["price"] == 25.0


def test_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_create_item_rejects_bad_price():
    response = client.post("/items", json={"name": "Broken", "price": "not-a-number"})
    assert response.status_code == 422
