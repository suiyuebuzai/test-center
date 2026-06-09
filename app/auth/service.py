from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User, Role, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictError, BusinessError


def register_user(db: Session, username: str, email: str, password: str) -> User:
    # 检查用户名和邮箱是否已存在
    existing = db.execute(
        select(User).where((User.username == username) | (User.email == email))
    ).scalar_one_or_none()
    if existing:
        raise ConflictError("用户名或邮箱已被注册")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.flush()  # 获取 user.id，但不提交事务

    # 第一个用户自动成为 admin，其余默认为 tester
    user_count = db.execute(select(User)).scalars().all()
    role_name = "admin" if len(user_count) == 1 else "tester"
    role = db.execute(select(Role).where(Role.name == role_name)).scalar_one()
    db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> str:
    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise BusinessError(code="INVALID_CREDENTIALS", message="用户名或密码错误")
    if not user.is_active:
        raise BusinessError(code="USER_INACTIVE", message="账号已被禁用")

    return create_access_token({"sub": str(user.id)})


def get_user_by_id(db: Session, user_id: str) -> User | None:
    import uuid
    return db.get(User, uuid.UUID(user_id))
