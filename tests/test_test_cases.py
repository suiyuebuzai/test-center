import pytest


@pytest.fixture
async def setup(client):
    """创建 admin 用户、登录、创建应用，返回 (token, app_id)。"""
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "admin123"
    })
    login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["data"]["access_token"]
    app_resp = await client.post("/api/v1/apps", json={"name": "TestApp", "code": "TA"},
                                  headers={"Authorization": f"Bearer {token}"})
    app_id = app_resp.json()["data"]["id"]
    return token, app_id


async def test_create_test_case(client, setup):
    token, app_id = setup
    resp = await client.post(f"/api/v1/apps/{app_id}/test-cases", json={
        "title": "登录-正确账密-成功",
        "priority": "P1",
        "category": "登录模块",
        "steps": [{"step": 1, "action": "输入正确账密", "expected": "登录成功"}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "登录-正确账密-成功"
    assert data["priority"] == "P1"


async def test_list_test_cases_with_filter(client, setup):
    token, app_id = setup
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/apps/{app_id}/test-cases",
                      json={"title": "用例1", "priority": "P0", "category": "登录"},
                      headers=headers)
    await client.post(f"/api/v1/apps/{app_id}/test-cases",
                      json={"title": "用例2", "priority": "P2", "category": "订单"},
                      headers=headers)

    resp = await client.get(f"/api/v1/apps/{app_id}/test-cases?priority=P0", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["items"][0]["title"] == "用例1"


async def test_soft_delete_test_case(client, setup):
    token, app_id = setup
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(f"/api/v1/apps/{app_id}/test-cases",
                                     json={"title": "待删用例"}, headers=headers)
    case_id = create_resp.json()["data"]["id"]

    await client.delete(f"/api/v1/test-cases/{case_id}", headers=headers)

    # 列表里查不到
    list_resp = await client.get(f"/api/v1/apps/{app_id}/test-cases", headers=headers)
    assert list_resp.json()["data"]["total"] == 0

    # 详情返回 404
    get_resp = await client.get(f"/api/v1/test-cases/{case_id}", headers=headers)
    assert get_resp.status_code == 404
