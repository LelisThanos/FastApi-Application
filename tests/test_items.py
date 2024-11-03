import pytest
from fastapi import status
from tests.utils import create_test_user, create_test_item, create_test_items


# Test item creation
def test_create_item(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.post(
        "/items/",
        json={"name": "New Item", "description": "Item Description", "price": 150.0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Item"
    assert response.json()["description"] == "Item Description"
    assert response.json()["price"] == 150.0

# Test retrieving items with pagination
def test_retrieve_items(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    for i in range(5):
        create_test_item(fakedb, user_id=user.id, name=f"Item {i}", description="Test Desc", price=50.0 + i)

    response = client.get("/items/?skip=0&limit=3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

# Test updating an item
def test_update_item(client, fakedb):
    user = create_test_user(fakedb)
    item = create_test_item(fakedb, user_id=user.id, name="Original Name", price=100.0)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.put(
        f"/items/{item.id}",
        json={"name": "Updated Name", "description": "Updated Desc", "price": 200.0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Name"
    assert response.json()["price"] == 200.0

# Test deleting an item
def test_delete_item(client, fakedb):
    user = create_test_user(fakedb)
    item = create_test_item(fakedb, user_id=user.id)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.delete(f"/items/{item.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(f"/items/{item.id}", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

# Test filtering by price range
def test_filter_items_by_price_range(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]
    create_test_items(fakedb, user_id=user.id)

    response = client.get(
        "/items/?min_price=10&max_price=20",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    for item in items:
        assert 10 <= item["price"] <= 20

# Test searching items by keyword
def test_search_items_by_keyword(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]
    create_test_items(fakedb, user_id=user.id)

    response = client.get(
        "/items/?query=Expensive",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "very very expensive Item"

# Test item creation with invalid data
def test_create_item_invalid_data(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.post(
        "/items/",
        json={"description": "Missing name and price"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post(
        "/items/",
        json={"name": "Invalid Price", "description": "This should fail", "price": "not-a-number"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test updating a non-existent item
def test_update_non_existent_item(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.put(
        "/items/999",
        json={"name": "Nonexistent Item", "description": "Should fail", "price": 50.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

# Test deleting a non-existent item
def test_delete_non_existent_item(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.delete("/items/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

# Test invalid pagination parameters
def test_invalid_pagination_parameters(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.get("/items/?skip=-1&limit=-5", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()

# Test invalid price range
def test_invalid_price_range(client, fakedb):
    user = create_test_user(fakedb)
    token = client.post("/token", data={"username": user.username, "password": "password"}).json()["access_token"]

    response = client.get("/items/?min_price=50&max_price=10", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Assuming the app checks this and returns 400
    assert response.json() == {"detail": "min_price cannot be greater than max_price"}

# Test accessing with an invalid token
def test_access_with_invalid_token(client):
    response = client.get("/items/", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
