import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import success, created
from app.core.deps import get_current_user, require_roles
from app.test_case import service
from app.test_case.schemas import TestCaseCreate, TestCaseUpdate, TestCaseResponse
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["测试用例"])


@router.post("/apps/{app_id}/test-cases")
def create_test_case(
    app_id: uuid.UUID,
    payload: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    tc = service.create_test_case(db, app_id, payload.model_dump(exclude_none=True), current_user.id)
    return created(TestCaseResponse.model_validate(tc).model_dump(mode="json"))


@router.get("/apps/{app_id}/test-cases")
def list_test_cases(
    app_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    priority: str | None = None,
    category: str | None = None,
    is_automated: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = service.list_test_cases(db, app_id, page, page_size, priority, category, is_automated)
    result["items"] = [TestCaseResponse.model_validate(tc).model_dump(mode="json") for tc in result["items"]]
    return success(result)


@router.get("/test-cases/{case_id}")
def get_test_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tc = service.get_test_case(db, case_id)
    return success(TestCaseResponse.model_validate(tc).model_dump(mode="json"))


@router.put("/test-cases/{case_id}")
def update_test_case(
    case_id: uuid.UUID,
    payload: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    tc = service.get_test_case(db, case_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(tc, field, value)
    db.commit()
    db.refresh(tc)
    return success(TestCaseResponse.model_validate(tc).model_dump(mode="json"))


@router.delete("/test-cases/{case_id}")
def delete_test_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    service.delete_test_case(db, case_id)
    return success(None, message="删除成功")
