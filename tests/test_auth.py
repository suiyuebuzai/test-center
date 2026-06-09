import pytest


async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "alice"
    assert "hashed_password" not in data["data"]


async def test_register_duplicate_username(client):
    payload = {"username": "alice", "email": "alice@example.com", "password": "pass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json={
        "username": "alice", "email": "alice2@example.com", "password": "pass123"
    })
    assert response.status_code == 409


async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "username": "bob", "email": "bob@example.com", "password": "mypassword"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "bob", "password": "mypassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "username": "carol", "email": "carol@example.com", "password": "correct"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "carol", "password": "wrong"
    })
    assert response.status_code == 400


async def test_get_me(client):
    await client.post("/api/v1/auth/register", json={
        "username": "dave", "email": "dave@example.com", "password": "pass"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "dave", "password": "pass"
    })
    token = login_resp.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "dave"


async def test_get_me_no_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)  # HTTPBearer returns 401 or 403 depending on FastAPI version
