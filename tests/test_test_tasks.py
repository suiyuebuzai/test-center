import pytest
from datetime import datetime, timezone


@pytest.fixture
async def setup(client):
    """创建 admin、登录、建应用、建版本、建用例，返回所需 ID。"""
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "admin123"
    })
    login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    app_resp = await client.post("/api/v1/apps", json={"name": "MyApp", "code": "MA"}, headers=headers)
    app_id = app_resp.json()["data"]["id"]

    ver_resp = await client.post(f"/api/v1/apps/{app_id}/versions",
                                  json={"name": "v1.0"}, headers=headers)
    version_id = ver_resp.json()["data"]["id"]

    case_resp = await client.post(f"/api/v1/apps/{app_id}/test-cases",
                                   json={"title": "用例A"}, headers=headers)
    case_id = case_resp.json()["data"]["id"]

    return token, app_id, version_id, case_id


async def test_create_test_task(client, setup):
    token, app_id, version_id, _ = setup
    resp = await client.post(f"/api/v1/apps/{app_id}/test-tasks", json={
        "name": "第一轮全量测试", "version_id": version_id,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "第一轮全量测试"
    assert resp.json()["data"]["status"] == "pending"


async def test_submit_execution(client, setup):
    token, app_id, version_id, case_id = setup
    headers = {"Authorization": f"Bearer {token}"}

    task_resp = await client.post(f"/api/v1/apps/{app_id}/test-tasks",
                                   json={"name": "任务1", "version_id": version_id}, headers=headers)
    task_id = task_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/test-tasks/{task_id}/executions", json={
        "test_case_id": case_id,
        "result": "fail",
        "actual_result": "页面报错 500",
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["data"]["result"] == "fail"


async def test_list_executions(client, setup):
    token, app_id, version_id, case_id = setup
    headers = {"Authorization": f"Bearer {token}"}

    task_resp = await client.post(f"/api/v1/apps/{app_id}/test-tasks",
                                   json={"name": "任务2", "version_id": version_id}, headers=headers)
    task_id = task_resp.json()["data"]["id"]

    await client.post(f"/api/v1/test-tasks/{task_id}/executions", json={
        "test_case_id": case_id, "result": "pass",
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }, headers=headers)

    resp = await client.get(f"/api/v1/test-tasks/{task_id}/executions", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
