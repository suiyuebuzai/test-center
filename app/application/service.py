import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.application import Application
from app.models.version import Version
from app.core.exceptions import NotFoundError, ConflictError


def create_application(db: Session, name: str, code: str, description: str | None,
                        created_by: uuid.UUID) -> Application:
    existing = db.execute(
        select(Application).where(
            (Application.name == name) | (Application.code == code.upper())
        ).where(Application.is_deleted == False)
    ).scalar_one_or_none()
    if existing:
        raise ConflictError("应用名称或 code 已存在")

    app = Application(
        name=name, code=code.upper(), description=description, created_by=created_by
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def list_applications(db: Session, page: int = 1, page_size: int = 20) -> dict:
    query = select(Application).where(Application.is_deleted == False)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    items = db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_application(db: Session, app_id: uuid.UUID) -> Application:
    app = db.execute(
        select(Application).where(Application.id == app_id, Application.is_deleted == False)
    ).scalar_one_or_none()
    if not app:
        raise NotFoundError("应用不存在")
    return app


def create_version(db: Session, app_id: uuid.UUID, name: str, description: str | None,
                   created_by: uuid.UUID) -> Version:
    get_application(db, app_id)  # 验证应用存在
    version = Version(app_id=app_id, name=name, description=description, created_by=created_by)
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def list_versions(db: Session, app_id: uuid.UUID) -> list:
    get_application(db, app_id)
    return db.execute(
        select(Version).where(Version.app_id == app_id)
    ).scalars().all()
