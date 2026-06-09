import pytest
from datetime import datetime, timezone


@pytest.fixture
async def setup(client):
    """注册 admin/developer/tester，建好应用+版本，返回 tokens 和 IDs。"""
    # admin（第一个注册的用户）
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@t.com", "password": "admin123"
    })
    login_a = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = login_a.json()["data"]["access_token"]
    ah = {"Authorization": f"Bearer {admin_token}"}

    # 建应用和版本
    app_resp = await client.post("/api/v1/apps", json={"name": "App", "code": "APP"}, headers=ah)
    app_id = app_resp.json()["data"]["id"]
    ver_resp = await client.post(f"/api/v1/apps/{app_id}/versions",
                                  json={"name": "v1.0"}, headers=ah)
    version_id = ver_resp.json()["data"]["id"]

    # developer 用户（admin 手动改角色，或直接用 admin 创建）
    await client.post("/api/v1/auth/register", json={
        "username": "dev1", "email": "dev1@t.com", "password": "dev123"
    })
    login_d = await client.post("/api/v1/auth/login", json={"username": "dev1", "password": "dev123"})
    dev_token = login_d.json()["data"]["access_token"]

    return admin_token, dev_token, app_id, version_id


async def test_create_defect(client, setup):
    admin_token, _, app_id, version_id = setup
    resp = await client.post(f"/api/v1/apps/{app_id}/defects", json={
        "title": "登录页报错",
        "severity": "high",
        "priority": "P1",
        "found_version_id": version_id,
        "steps_to_reproduce": "1.打开登录页 2.点登录",
        "actual_result": "500 Internal Server Error",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "登录页报错"
    assert data["status"] == "new"
    assert data["defect_no"].startswith("APP-")


async def test_defect_no_auto_increment(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    r1 = await client.post(f"/api/v1/apps/{app_id}/defects",
                            json={"title": "Bug1", "found_version_id": version_id}, headers=headers)
    r2 = await client.post(f"/api/v1/apps/{app_id}/defects",
                            json={"title": "Bug2", "found_version_id": version_id}, headers=headers)
    no1 = r1.json()["data"]["defect_no"]
    no2 = r2.json()["data"]["defect_no"]
    assert no1 != no2
    assert no1 == "APP-0001"
    assert no2 == "APP-0002"


async def test_transition_new_to_assigned(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/defects/{defect_id}/transitions", json={
        "to_status": "assigned", "comment": "指派处理"
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "assigned"


async def test_invalid_transition_raises_400(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    # new → closed 是非法跳转
    resp = await client.post(f"/api/v1/defects/{defect_id}/transitions",
                              json={"to_status": "closed"}, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TRANSITION"


async def test_add_and_list_comments(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    await client.post(f"/api/v1/defects/{defect_id}/comments",
                      json={"content": "已确认，指派开发"}, headers=headers)

    detail = await client.get(f"/api/v1/defects/{defect_id}", headers=headers)
    assert len(detail.json()["data"]["comments"]) == 1
    assert detail.json()["data"]["comments"][0]["content"] == "已确认，指派开发"


async def test_defect_status_history_recorded(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    await client.post(f"/api/v1/defects/{defect_id}/transitions",
                      json={"to_status": "assigned"}, headers=headers)

    history_resp = await client.get(f"/api/v1/defects/{defect_id}/history", headers=headers)
    history = history_resp.json()["data"]
    # history includes the creation entry (from_status=None) + the transition
    assert len(history) == 2
    assert history[-1]["from_status"] == "new"
    assert history[-1]["to_status"] == "assigned"
