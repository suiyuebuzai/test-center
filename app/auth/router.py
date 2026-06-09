from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import success, created
from app.core.deps import get_current_user
from app.auth import service
from app.auth.schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = service.register_user(db, payload.username, payload.email, payload.password)
    return created(UserResponse.model_validate(user).model_dump(mode="json"))


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = service.login_user(db, payload.username, payload.password)
    return success(TokenResponse(access_token=token).model_dump(mode="json"))


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success(UserResponse.model_validate(current_user).model_dump(mode="json"))
