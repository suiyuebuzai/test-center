import pytest


@pytest.fixture
async def admin_token(client):
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "admin123"
    })
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    return resp.json()["data"]["access_token"]


@pytest.fixture
async def tester_token(client, admin_token):
    await client.post("/api/v1/auth/register", json={
        "username": "tester1", "email": "tester1@test.com", "password": "tester123"
    })
    resp = await client.post("/api/v1/auth/login", json={"username": "tester1", "password": "tester123"})
    return resp.json()["data"]["access_token"]


async def test_create_app_as_admin(client, admin_token):
    resp = await client.post("/api/v1/apps", json={
        "name": "电商平台", "code": "MALL", "description": "主要业务系统"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "电商平台"
    assert data["code"] == "MALL"


async def test_create_app_as_tester_forbidden(client, tester_token):
    resp = await client.post("/api/v1/apps", json={
        "name": "App", "code": "APP"
    }, headers={"Authorization": f"Bearer {tester_token}"})
    assert resp.status_code == 403


async def test_list_apps(client, admin_token):
    await client.post("/api/v1/apps", json={"name": "App1", "code": "A1"},
                      headers={"Authorization": f"Bearer {admin_token}"})
    await client.post("/api/v1/apps", json={"name": "App2", "code": "A2"},
                      headers={"Authorization": f"Bearer {admin_token}"})
    resp = await client.get("/api/v1/apps", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2


async def test_create_version(client, admin_token):
    app_resp = await client.post("/api/v1/apps", json={"name": "MyApp", "code": "MA"},
                                  headers={"Authorization": f"Bearer {admin_token}"})
    app_id = app_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/apps/{app_id}/versions", json={
        "name": "v1.0.0", "description": "首个版本"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "v1.0.0"


async def test_get_app_not_found(client, admin_token):
    resp = await client.get(
        "/api/v1/apps/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 404
