import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_signup_and_login():
    response = client.post("/auth/signup", json={
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "strongpassword",
        "role": "Admin"
    })
    assert response.status_code == 200
    result = response.json()
    assert result["email"] == "admin@example.com"

    response = client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "strongpassword"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"

    response = client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "strongpassword",
        "role": "Admin"
    })
    assert response.status_code == 200
    assert response.json()["access_token"]

    response = client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "strongpassword",
        "role": "Member"
    })
    assert response.status_code == 401
