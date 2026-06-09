from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.auth.service import get_user_by_id

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析 JWT，返回当前登录用户。Token 无效时返回 401。"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("token 缺少 sub 字段")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


def require_roles(*role_names: str):
    """工厂函数：返回一个依赖，要求当前用户拥有指定角色之一。"""
    def _check(current_user: User = Depends(get_current_user)) -> User:
        user_roles = current_user.role_names
        if not any(r in user_roles for r in role_names):
            raise ForbiddenError(f"需要角色：{', '.join(role_names)}")
        return current_user
    return _check
