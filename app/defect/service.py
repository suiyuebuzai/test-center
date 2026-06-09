import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.defect import Defect, DefectComment, DefectStatusHistory
from app.models.application import Application
from app.core.exceptions import NotFoundError
from app.defect.state_machine import validate_transition


def _get_app_or_404(db: Session, app_id: uuid.UUID) -> Application:
    app = db.execute(
        select(Application).where(Application.id == app_id, Application.is_deleted == False)
    ).scalar_one_or_none()
    if not app:
        raise NotFoundError("应用不存在")
    return app


def _generate_defect_no(db: Session, app_id: uuid.UUID, app_code: str) -> str:
    count = db.execute(
        select(func.count()).select_from(Defect).where(Defect.app_id == app_id)
    ).scalar() or 0
    return f"{app_code}-{count + 1:04d}"


def create_defect(db: Session, app_id: uuid.UUID, data: dict,
                  reporter_id: uuid.UUID) -> Defect:
    app = _get_app_or_404(db, app_id)
    defect_no = _generate_defect_no(db, app_id, app.code)
    defect = Defect(
        app_id=app_id,
        defect_no=defect_no,
        reporter_id=reporter_id,
        **data,
    )
    db.add(defect)
    db.flush()

    # 记录初始状态到历史
    db.add(DefectStatusHistory(
        defect_id=defect.id,
        from_status=None,
        to_status="new",
        changed_by=reporter_id,
        comment="创建缺陷",
    ))
    db.commit()
    db.refresh(defect)
    return defect


def get_defect(db: Session, defect_id: uuid.UUID) -> Defect:
    defect = db.execute(
        select(Defect).where(Defect.id == defect_id, Defect.is_deleted == False)
    ).scalar_one_or_none()
    if not defect:
        raise NotFoundError("缺陷不存在")
    return defect


def list_defects(db: Session, app_id: uuid.UUID, page: int = 1, page_size: int = 20,
                 status: str | None = None, severity: str | None = None,
                 assignee_id: uuid.UUID | None = None) -> dict:
    _get_app_or_404(db, app_id)
    query = select(Defect).where(Defect.app_id == app_id, Defect.is_deleted == False)
    if status:
        query = query.where(Defect.status == status)
    if severity:
        query = query.where(Defect.severity == severity)
    if assignee_id:
        query = query.where(Defect.assignee_id == assignee_id)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    items = db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def transition_defect(db: Session, defect_id: uuid.UUID, to_status: str,
                      user_id: uuid.UUID, user_roles: list[str],
                      assignee_id: uuid.UUID | None = None,
                      comment: str | None = None) -> Defect:
    defect = get_defect(db, defect_id)
    validate_transition(defect.status, to_status, user_roles)  # 抛异常则终止

    old_status = defect.status
    defect.status = to_status
    if assignee_id:
        defect.assignee_id = assignee_id
    if to_status == "closed":
        defect.closed_at = datetime.utcnow()

    db.add(DefectStatusHistory(
        defect_id=defect.id,
        from_status=old_status,
        to_status=to_status,
        changed_by=user_id,
        comment=comment,
    ))
    db.commit()
    db.refresh(defect)
    return defect


def add_comment(db: Session, defect_id: uuid.UUID, content: str,
                author_id: uuid.UUID) -> DefectComment:
    get_defect(db, defect_id)  # 验证缺陷存在
    comment = DefectComment(defect_id=defect_id, content=content, author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_status_history(db: Session, defect_id: uuid.UUID) -> list:
    get_defect(db, defect_id)
    return db.execute(
        select(DefectStatusHistory)
        .where(DefectStatusHistory.defect_id == defect_id)
        .order_by(DefectStatusHistory.changed_at)
    ).scalars().all()
