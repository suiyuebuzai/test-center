import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.test_task import TestTask
from app.models.execution import TaskExecution
from app.models.version import Version
from app.core.exceptions import NotFoundError


def create_test_task(db: Session, app_id: uuid.UUID, data: dict,
                     created_by: uuid.UUID) -> TestTask:
    # 验证 version 属于该 app
    version = db.execute(
        select(Version).where(Version.id == data["version_id"], Version.app_id == app_id)
    ).scalar_one_or_none()
    if not version:
        raise NotFoundError("版本不存在或不属于该应用")

    task = TestTask(app_id=app_id, created_by=created_by, **data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_test_task(db: Session, task_id: uuid.UUID) -> TestTask:
    task = db.get(TestTask, task_id)
    if not task:
        raise NotFoundError("测试任务不存在")
    return task


def list_test_tasks(db: Session, app_id: uuid.UUID) -> list:
    return db.execute(
        select(TestTask).where(TestTask.app_id == app_id)
    ).scalars().all()


def create_execution(db: Session, task_id: uuid.UUID, data: dict,
                     executor_id: uuid.UUID) -> TaskExecution:
    get_test_task(db, task_id)
    execution = TaskExecution(task_id=task_id, executor_id=executor_id, **data)
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def list_executions(db: Session, task_id: uuid.UUID) -> list:
    get_test_task(db, task_id)
    return db.execute(
        select(TaskExecution).where(TaskExecution.task_id == task_id)
    ).scalars().all()
