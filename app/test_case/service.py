import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from app.models.test_case import TestCase
from app.models.application import Application
from app.core.exceptions import NotFoundError


def _get_app_or_404(db: Session, app_id: uuid.UUID) -> Application:
    app = db.execute(
        select(Application).where(Application.id == app_id, Application.is_deleted == False)
    ).scalar_one_or_none()
    if not app:
        raise NotFoundError("应用不存在")
    return app


def create_test_case(db: Session, app_id: uuid.UUID, data: dict,
                     created_by: uuid.UUID) -> TestCase:
    _get_app_or_404(db, app_id)
    tc = TestCase(app_id=app_id, created_by=created_by, **data)
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


def list_test_cases(db: Session, app_id: uuid.UUID, page: int = 1, page_size: int = 20,
                    priority: str | None = None, category: str | None = None,
                    is_automated: bool | None = None) -> dict:
    _get_app_or_404(db, app_id)
    query = select(TestCase).where(TestCase.app_id == app_id, TestCase.is_deleted == False)
    if priority:
        query = query.where(TestCase.priority == priority)
    if category:
        query = query.where(TestCase.category == category)
    if is_automated is not None:
        query = query.where(TestCase.is_automated == is_automated)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    items = db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_test_case(db: Session, case_id: uuid.UUID) -> TestCase:
    tc = db.execute(
        select(TestCase).where(TestCase.id == case_id, TestCase.is_deleted == False)
    ).scalar_one_or_none()
    if not tc:
        raise NotFoundError("测试用例不存在")
    return tc


def delete_test_case(db: Session, case_id: uuid.UUID) -> None:
    tc = get_test_case(db, case_id)
    tc.is_deleted = True
    tc.deleted_at = datetime.utcnow()
    db.commit()
