import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import success, created
from app.core.deps import get_current_user, require_roles
from app.application import service
from app.application.schemas import (
    AppCreate, AppUpdate, AppResponse, VersionCreate, VersionResponse, PaginatedResponse
)
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["应用管理"])


@router.post("/apps")
def create_app(
    payload: AppCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    app = service.create_application(db, payload.name, payload.code,
                                      payload.description, current_user.id)
    return created(AppResponse.model_validate(app).model_dump(mode="json"))


@router.get("/apps")
def list_apps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = service.list_applications(db, page, page_size)
    result["items"] = [AppResponse.model_validate(a).model_dump(mode="json") for a in result["items"]]
    return success(result)


@router.get("/apps/{app_id}")
def get_app(
    app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = service.get_application(db, app_id)
    return success(AppResponse.model_validate(app).model_dump(mode="json"))


@router.get("/apps/{app_id}/versions")
def list_versions(
    app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    versions = service.list_versions(db, app_id)
    return success([VersionResponse.model_validate(v).model_dump(mode="json") for v in versions])


@router.post("/apps/{app_id}/versions")
def create_version(
    app_id: uuid.UUID,
    payload: VersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    version = service.create_version(db, app_id, payload.name, payload.description, current_user.id)
    return created(VersionResponse.model_validate(version).model_dump(mode="json"))
