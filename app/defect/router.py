import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import success, created
from app.core.deps import get_current_user, require_roles
from app.defect import service
from app.defect.schemas import (
    DefectCreate, DefectTransition, CommentCreate,
    DefectResponse, DefectListResponse, CommentResponse, StatusHistoryResponse
)
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["缺陷管理"])


@router.post("/apps/{app_id}/defects")
def create_defect(
    app_id: uuid.UUID,
    payload: DefectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    defect = service.create_defect(db, app_id, payload.model_dump(exclude_none=True), current_user.id)
    return created(DefectResponse.model_validate(defect).model_dump(mode="json"))


@router.get("/apps/{app_id}/defects")
def list_defects(
    app_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = service.list_defects(db, app_id, page, page_size, status, severity)
    result["items"] = [DefectListResponse.model_validate(d).model_dump(mode="json") for d in result["items"]]
    return success(result)


@router.get("/defects/{defect_id}")
def get_defect(
    defect_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    defect = service.get_defect(db, defect_id)
    return success(DefectResponse.model_validate(defect).model_dump(mode="json"))


@router.post("/defects/{defect_id}/transitions")
def transition_defect(
    defect_id: uuid.UUID,
    payload: DefectTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    defect = service.transition_defect(
        db, defect_id, payload.to_status, current_user.id,
        current_user.role_names, payload.assignee_id, payload.comment,
    )
    return success(DefectResponse.model_validate(defect).model_dump(mode="json"))


@router.post("/defects/{defect_id}/comments")
def add_comment(
    defect_id: uuid.UUID,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = service.add_comment(db, defect_id, payload.content, current_user.id)
    return created(CommentResponse.model_validate(comment).model_dump(mode="json"))


@router.get("/defects/{defect_id}/history")
def get_history(
    defect_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = service.get_status_history(db, defect_id)
    return success([StatusHistoryResponse.model_validate(h).model_dump(mode="json") for h in history])
