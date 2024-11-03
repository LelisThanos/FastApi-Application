from datetime import timedelta

import pytest
from fastapi import status

from app.auth.utils import create_access_token
from tests.utils import create_test_user

USERNAME = "testuser"
PASSWORD = "testpassword"
EMAIL = "testuser@example.com"

# Test token generation
def test_token_generation(client, fakedb):
    create_test_user(fakedb, username=USERNAME, password=PASSWORD, email=EMAIL)

    response = client.post(
        "/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Test invalid token generation (wrong credentials)
def test_invalid_token_generation(client):
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}

# Test accessing protected route with valid token
def test_access_protected_route_with_valid_token(client, fakedb):
    create_test_user(db=fakedb, username=USERNAME, password=PASSWORD, email=EMAIL)

    response = client.post(
        "/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]

    protected_response = client.get(
        "/items/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_response.status_code == status.HTTP_200_OK

# Test invalid token
def test_access_protected_route_with_invalid_token(client):
    response = client.get(
        "/items/",
        headers={"Authorization": "Bearer IAmAnInvalid-Token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}

def test_expired_token(client, fakedb):
    # Create a test user
    user = create_test_user(fakedb)

    # Generate an expired token by setting a negative expiration time
    token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(seconds=-1))

    # Attempt to access a protected route with the expired token
    response = client.get("/items/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
