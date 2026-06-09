import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import success, created
from app.core.deps import get_current_user, require_roles
from app.test_task import service
from app.test_task.schemas import (
    TestTaskCreate, TestTaskResponse, ExecutionCreate, ExecutionResponse
)
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["测试任务"])


@router.post("/apps/{app_id}/test-tasks")
def create_task(
    app_id: uuid.UUID,
    payload: TestTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    task = service.create_test_task(db, app_id, payload.model_dump(exclude_none=True), current_user.id)
    return created(TestTaskResponse.model_validate(task).model_dump(mode="json"))


@router.get("/apps/{app_id}/test-tasks")
def list_tasks(
    app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = service.list_test_tasks(db, app_id)
    return success([TestTaskResponse.model_validate(t).model_dump(mode="json") for t in tasks])


@router.get("/test-tasks/{task_id}")
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = service.get_test_task(db, task_id)
    return success(TestTaskResponse.model_validate(task).model_dump(mode="json"))


@router.post("/test-tasks/{task_id}/executions")
def create_execution(
    task_id: uuid.UUID,
    payload: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    execution = service.create_execution(
        db, task_id, payload.model_dump(exclude_none=True), current_user.id
    )
    return created(ExecutionResponse.model_validate(execution).model_dump(mode="json"))


@router.get("/test-tasks/{task_id}/executions")
def list_executions(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    executions = service.list_executions(db, task_id)
    return success([ExecutionResponse.model_validate(e).model_dump(mode="json") for e in executions])
