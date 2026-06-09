# test-center Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade FastAPI test management platform with JWT auth, PostgreSQL, full CRUD for the functional testing core (12 tables), and pytest test coverage.

**Architecture:** Modular monolith — module-first structure (auth, application, test_case, test_task, defect), shared SQLAlchemy models in `app/models/`, shared infrastructure in `app/core/`. Router→Service→ORM three-layer. No repository layer in Phase 1.

**Tech Stack:** Python 3.11, FastAPI 0.111, SQLAlchemy 2.0 (sync), Alembic, PostgreSQL 15, python-jose, passlib[bcrypt], pytest + httpx, Docker Compose.

**Working directory:** `C:\1AI\personal-md-database\yangli2026\work\20260609test-center`

---

## File Map

```
test-center/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── deps.py
│   │   ├── exceptions.py
│   │   └── responses.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── application.py
│   │   ├── version.py
│   │   ├── test_case.py
│   │   ├── test_task.py
│   │   ├── execution.py
│   │   ├── associations.py
│   │   └── defect.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── test_case/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── test_task/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   └── defect/
│       ├── __init__.py
│       ├── router.py
│       ├── service.py
│       ├── schemas.py
│       └── state_machine.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_applications.py
│   ├── test_test_cases.py
│   ├── test_test_tasks.py
│   ├── test_state_machine.py
│   └── test_defects.py
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── .env
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## Task 1: 项目骨架 & 环境配置

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.env.example` 和 `.env`
- Create: `app/__init__.py`（及所有模块的 `__init__.py`，全部空文件）
- Create: `app/main.py`
- Create: `app/core/config.py`

- [ ] **Step 1: 创建虚拟环境并安装依赖**

```bash
cd /c/1AI/personal-md-database/yangli2026/work/20260609test-center
python -m venv venv
source venv/Scripts/activate   # Windows bash
# 或 Windows CMD: venv\Scripts\activate
```

创建 `requirements.txt`：

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.7.1
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.7
```

```bash
pip install -r requirements.txt
```

Expected: 所有包安装成功，无报错。

- [ ] **Step 2: 创建 pyproject.toml**

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.black]
line-length = 88

[tool.pytest.ini_options]
asyncio_mode = "auto"
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 3: 创建 .env.example 和 .env**

`.env.example`：

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/test_center
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/test_center_test
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

`.env`（本地开发用，不提交 git）：

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/test_center
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/test_center_test
SECRET_KEY=dev-secret-key-not-for-production-use-only
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- [ ] **Step 4: 创建 app/core/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str = ""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = {"env_file": ".env"}


settings = Settings()
```

- [ ] **Step 5: 创建所有 __init__.py（空文件）和 app/main.py 骨架**

```bash
mkdir -p app/core app/models app/auth app/application app/test_case app/test_task app/defect
mkdir -p tests alembic/versions
touch app/__init__.py app/core/__init__.py app/models/__init__.py
touch app/auth/__init__.py app/application/__init__.py
touch app/test_case/__init__.py app/test_task/__init__.py app/defect/__init__.py
touch tests/__init__.py
```

`app/main.py`：

```python
from fastapi import FastAPI

app = FastAPI(
    title="test-center",
    description="测试管理平台 API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 6: 验证服务能启动**

```bash
uvicorn app.main:app --reload
```

Expected: 看到 `Application startup complete.`，浏览器访问 `http://localhost:8000/health` 返回 `{"status":"ok"}`，访问 `http://localhost:8000/docs` 看到 Swagger UI。

- [ ] **Step 7: 提交**

```bash
git init
echo "venv/" > .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
git add .
git commit -m "feat: 初始化项目骨架"
```

---

## Task 2: 核心基础设施

**Files:**
- Create: `app/core/database.py`
- Create: `app/core/exceptions.py`
- Create: `app/core/responses.py`
- Create: `app/core/security.py`
- Modify: `app/main.py`（注册全局异常 handler）

- [ ] **Step 1: 创建 app/core/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # 自动检测连接是否存活
    echo=False,           # 调试时改为 True 可看到 SQL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI 依赖注入：获取数据库 Session，请求结束后自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: 创建 app/core/exceptions.py**

```python
class NotFoundError(Exception):
    """资源不存在 → HTTP 404"""
    def __init__(self, message: str = "资源不存在"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """无权限 → HTTP 403"""
    def __init__(self, message: str = "无访问权限"):
        self.message = message
        super().__init__(self.message)


class BusinessError(Exception):
    """业务规则违反 → HTTP 400（如非法状态流转）"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


class ConflictError(Exception):
    """唯一约束冲突 → HTTP 409（如应用 code 重复）"""
    def __init__(self, message: str = "资源已存在"):
        self.message = message
        super().__init__(self.message)
```

- [ ] **Step 3: 创建 app/core/responses.py**

```python
from typing import Any
from fastapi.responses import JSONResponse


def success(data: Any, message: str = "操作成功", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data, "message": message},
    )


def created(data: Any, message: str = "创建成功") -> JSONResponse:
    return success(data, message, status_code=201)
```

- [ ] **Step 4: 创建 app/core/security.py**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """解码 JWT，失败时抛出 JWTError（由调用方处理）。"""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
```

- [ ] **Step 5: 更新 app/main.py，注册全局异常 handler**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import NotFoundError, ForbiddenError, BusinessError, ConflictError

app = FastAPI(
    title="test-center",
    description="测试管理平台 API",
    version="0.1.0",
)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": {"code": "NOT_FOUND", "message": exc.message}},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(
        status_code=403,
        content={"success": False, "error": {"code": "FORBIDDEN", "message": exc.message}},
    )


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={"success": False, "error": {"code": "CONFLICT", "message": exc.message}},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 6: 提交**

```bash
git add app/core/ app/main.py
git commit -m "feat: 添加核心基础设施（database、exceptions、responses、security）"
```

---

## Task 3: SQLAlchemy 数据模型

**Files:**
- Create: `app/models/base.py`
- Create: `app/models/user.py`
- Create: `app/models/application.py`
- Create: `app/models/version.py`
- Create: `app/models/test_case.py`
- Create: `app/models/test_task.py`
- Create: `app/models/execution.py`
- Create: `app/models/associations.py`
- Create: `app/models/defect.py`
- Modify: `app/models/__init__.py`

- [ ] **Step 1: 创建 app/models/base.py**

```python
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """为表自动添加 created_at 和 updated_at 字段。"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SoftDeleteMixin:
    """为表添加软删除支持。"""
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

- [ ] **Step 2: 创建 app/models/user.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, SmallInteger, ForeignKey, DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(100))

    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="role")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user", foreign_keys="UserRole.user_id"
    )

    @property
    def role_names(self) -> list[str]:
        return [ur.role.name for ur in self.user_roles if ur.role]


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.id"), primary_key=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    granted_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    user: Mapped["User"] = relationship(
        back_populates="user_roles", foreign_keys=[user_id]
    )
    role: Mapped["Role"] = relationship(back_populates="user_roles")
```

- [ ] **Step 3: 创建 app/models/application.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Application(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    versions: Mapped[list["Version"]] = relationship(back_populates="application")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="application")
    test_tasks: Mapped[list["TestTask"]] = relationship(back_populates="application")
    defects: Mapped[list["Defect"]] = relationship(
        back_populates="application", foreign_keys="Defect.app_id"
    )
```

- [ ] **Step 4: 创建 app/models/version.py**

```python
import uuid
from datetime import date
from sqlalchemy import String, Text, ForeignKey, Date
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint
from app.models.base import Base, TimestampMixin


class Version(Base, TimestampMixin):
    __tablename__ = "versions"
    __table_args__ = (UniqueConstraint("app_id", "name", name="uq_version_app_name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    app_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="planning", nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    application: Mapped["Application"] = relationship(back_populates="versions")
    test_tasks: Mapped[list["TestTask"]] = relationship(back_populates="version")
```

- [ ] **Step 5: 创建 app/models/test_case.py**

```python
import uuid
from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy import Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class TestCase(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    app_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    preconditions: Mapped[str | None] = mapped_column(Text)
    steps: Mapped[list | None] = mapped_column(JSON)  # [{step, action, expected}]
    expected_result: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(5), default="P2", nullable=False)
    case_type: Mapped[str] = mapped_column(String(20), default="functional", nullable=False)
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    application: Mapped["Application"] = relationship(back_populates="test_cases")
    executions: Mapped[list["TaskExecution"]] = relationship(back_populates="test_case")
    defects: Mapped[list["Defect"]] = relationship(
        secondary="test_case_defects", back_populates="test_cases"
    )
```

- [ ] **Step 6: 创建 app/models/test_task.py**

```python
import uuid
from datetime import date
from sqlalchemy import String, Text, ForeignKey, Date
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class TestTask(Base, TimestampMixin):
    __tablename__ = "test_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    app_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("versions.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    application: Mapped["Application"] = relationship(back_populates="test_tasks")
    version: Mapped["Version"] = relationship(back_populates="test_tasks")
    executions: Mapped[list["TaskExecution"]] = relationship(back_populates="task")
```

- [ ] **Step 7: 创建 app/models/execution.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class TaskExecution(Base, TimestampMixin):
    __tablename__ = "task_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("test_tasks.id"), nullable=False
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("test_cases.id"), nullable=False
    )
    executor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    result: Mapped[str] = mapped_column(String(10), nullable=False)
    actual_result: Mapped[str | None] = mapped_column(Text)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    task: Mapped["TestTask"] = relationship(back_populates="executions")
    test_case: Mapped["TestCase"] = relationship(back_populates="executions")
```

- [ ] **Step 8: 创建 app/models/associations.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import Table, Column, ForeignKey, DateTime
from sqlalchemy import Uuid
from app.models.base import Base

# 测试用例 ↔ 缺陷 多对多中间表
test_case_defects = Table(
    "test_case_defects",
    Base.metadata,
    Column("test_case_id", Uuid(as_uuid=True), ForeignKey("test_cases.id"), primary_key=True),
    Column("defect_id", Uuid(as_uuid=True), ForeignKey("defects.id"), primary_key=True),
    Column("linked_by", Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True),
    Column("linked_at", DateTime(timezone=True), default=datetime.utcnow),
)
```

- [ ] **Step 9: 创建 app/models/defect.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Defect(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "defects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    defect_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    app_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    steps_to_reproduce: Mapped[str | None] = mapped_column(Text)
    expected_result: Mapped[str | None] = mapped_column(Text)
    actual_result: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)
    priority: Mapped[str] = mapped_column(String(5), default="P2", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="new", nullable=False)
    found_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("versions.id"), nullable=False
    )
    fix_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("versions.id"), nullable=True
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    source_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    application: Mapped["Application"] = relationship(
        back_populates="defects", foreign_keys=[app_id]
    )
    found_version: Mapped["Version"] = relationship(foreign_keys=[found_version_id])
    fix_version: Mapped["Version | None"] = relationship(foreign_keys=[fix_version_id])
    reporter: Mapped["User"] = relationship(foreign_keys=[reporter_id])
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id])
    comments: Mapped[list["DefectComment"]] = relationship(
        back_populates="defect", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["DefectStatusHistory"]] = relationship(
        back_populates="defect", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list["TestCase"]] = relationship(
        secondary="test_case_defects", back_populates="defects"
    )


class DefectComment(Base, TimestampMixin):
    __tablename__ = "defect_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    defect_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("defects.id"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    defect: Mapped["Defect"] = relationship(back_populates="comments")


class DefectStatusHistory(Base):
    __tablename__ = "defect_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    defect_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("defects.id"), nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    defect: Mapped["Defect"] = relationship(back_populates="status_history")
```

- [ ] **Step 10: 更新 app/models/__init__.py（让 Alembic 能发现所有模型）**

```python
# 导入所有模型，确保 Alembic autogenerate 能检测到所有表
from app.models.base import Base
from app.models.user import User, Role, UserRole
from app.models.application import Application
from app.models.version import Version
from app.models.test_case import TestCase
from app.models.test_task import TestTask
from app.models.execution import TaskExecution
from app.models.associations import test_case_defects
from app.models.defect import Defect, DefectComment, DefectStatusHistory

__all__ = [
    "Base",
    "User", "Role", "UserRole",
    "Application",
    "Version",
    "TestCase",
    "TestTask",
    "TaskExecution",
    "test_case_defects",
    "Defect", "DefectComment", "DefectStatusHistory",
]
```

- [ ] **Step 11: 提交**

```bash
git add app/models/
git commit -m "feat: 添加所有 SQLAlchemy 数据模型（12 张表）"
```

---

## Task 4: Alembic 迁移配置 & 建表

**Files:**
- Create: `alembic.ini`
- Modify: `alembic/env.py`
- Create: `alembic/versions/<hash>_initial.py`（自动生成）

- [ ] **Step 1: 初始化 Alembic**

```bash
alembic init alembic
```

Expected: 生成 `alembic.ini` 和 `alembic/` 目录。

- [ ] **Step 2: 配置 alembic.ini（修改 sqlalchemy.url 行）**

打开 `alembic.ini`，找到这一行并修改：

```ini
# 原来是：sqlalchemy.url = driver://user:pass@localhost/dbname
# 改为（从环境变量读取，在 env.py 里处理，这里留空或注释）
sqlalchemy.url =
```

- [ ] **Step 3: 修改 alembic/env.py**

将 `alembic/env.py` 替换为以下内容：

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 导入所有模型（让 autogenerate 能检测到所有表）
from app.models import Base  # noqa: F401  这行触发所有模型的导入
from app.core.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置数据库 URL（从 .env 读取）
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: 确保 PostgreSQL 数据库存在**

```bash
# 连接 PostgreSQL 并创建两个数据库（开发 + 测试）
psql -U postgres -c "CREATE DATABASE test_center;"
psql -U postgres -c "CREATE DATABASE test_center_test;"
```

Expected: `CREATE DATABASE` 输出，无报错。

- [ ] **Step 5: 生成初始迁移文件**

```bash
alembic revision --autogenerate -m "initial_schema"
```

Expected: 在 `alembic/versions/` 下生成一个 `xxxx_initial_schema.py`，打开检查里面是否包含所有表的 `create_table` 语句（应有 12 张表）。

- [ ] **Step 6: 执行迁移，建表**

```bash
alembic upgrade head
```

Expected: 看到每张表的 `Running upgrade -> xxxx` 输出，无报错。

用 psql 验证：

```bash
psql -U postgres -d test_center -c "\dt"
```

Expected: 列出 12 张表（applications, defect_comments, defect_status_history, defects, roles, task_executions, test_case_defects, test_cases, test_tasks, user_roles, users, versions）。

- [ ] **Step 7: 提交**

```bash
git add alembic/ alembic.ini
git commit -m "feat: Alembic 初始迁移，建立 12 张核心表"
```

---

## Task 5: 认证模块（TDD）

**Files:**
- Create: `tests/conftest.py`
- Create: `app/auth/schemas.py`
- Create: `app/auth/service.py`
- Create: `app/core/deps.py`
- Create: `app/auth/router.py`
- Modify: `app/main.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: 创建 tests/conftest.py（测试基础设施）**

```python
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.core.config import settings
from app.models.base import Base
from app.models.user import Role

TEST_DATABASE_URL = settings.test_database_url or settings.database_url.replace(
    "/test_center", "/test_center_test"
)

# 测试引擎（连接测试数据库）
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """每次测试会话开始时建表，结束后不删（方便调试）。"""
    Base.metadata.create_all(bind=test_engine)
    # 预置角色数据
    with Session(test_engine) as session:
        if not session.get(Role, 1):
            session.add_all([
                Role(id=1, name="admin", description="管理员"),
                Role(id=2, name="tester", description="测试人员"),
                Role(id=3, name="developer", description="开发人员"),
                Role(id=4, name="readonly", description="只读用户"),
            ])
            session.commit()
    yield


@pytest.fixture(autouse=True)
def clean_tables():
    """每个测试结束后清空所有业务数据（保留 roles）。"""
    yield
    with test_engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE task_executions RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE test_case_defects RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE defect_status_history RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE defect_comments RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE defects RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE test_tasks RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE test_cases RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE versions RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE applications RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE user_roles RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        conn.commit()


@pytest.fixture
def db():
    """每个测试用例获取一个独立的数据库 Session。"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
async def client(db):
    """FastAPI 测试客户端，注入测试数据库 Session。"""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

- [ ] **Step 2: 写失败测试（test_auth.py）**

创建 `tests/test_auth.py`：

```python
import pytest


async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "alice"
    assert "hashed_password" not in data["data"]


async def test_register_duplicate_username(client):
    payload = {"username": "alice", "email": "alice@example.com", "password": "pass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json={
        "username": "alice", "email": "alice2@example.com", "password": "pass123"
    })
    assert response.status_code == 409


async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "username": "bob", "email": "bob@example.com", "password": "mypassword"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "bob", "password": "mypassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "username": "carol", "email": "carol@example.com", "password": "correct"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "carol", "password": "wrong"
    })
    assert response.status_code == 401


async def test_get_me(client):
    await client.post("/api/v1/auth/register", json={
        "username": "dave", "email": "dave@example.com", "password": "pass"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "dave", "password": "pass"
    })
    token = login_resp.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "dave"


async def test_get_me_no_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
```

- [ ] **Step 3: 运行测试，确认全部失败**

```bash
pytest tests/test_auth.py -v
```

Expected: 全部 FAILED，原因是路由不存在（404）。

- [ ] **Step 4: 创建 app/auth/schemas.py**

```python
from pydantic import BaseModel, EmailStr
import uuid


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    roles: list[str] = []

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- [ ] **Step 5: 创建 app/auth/service.py**

```python
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
```

- [ ] **Step 6: 创建 app/core/deps.py**

```python
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
```

- [ ] **Step 7: 创建 app/auth/router.py**

```python
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
    return created(UserResponse.model_validate(user).model_dump())


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = service.login_user(db, payload.username, payload.password)
    return success(TokenResponse(access_token=token).model_dump())


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success(UserResponse.model_validate(current_user).model_dump())
```

- [ ] **Step 8: 更新 app/main.py，注册 auth 路由**

在 `app/main.py` 末尾添加：

```python
from app.auth.router import router as auth_router
app.include_router(auth_router)
```

- [ ] **Step 9: 修复 UserResponse 的 roles 字段**

`UserResponse.model_validate(user)` 需要能拿到 `roles` 字段。在 `app/auth/schemas.py` 的 `UserResponse` 中，roles 需要从 `user.role_names` 获取。用一个 validator 处理：

```python
from pydantic import BaseModel, EmailStr, model_validator
import uuid


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    roles: list[str] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_roles(cls, data):
        if hasattr(data, "role_names"):
            data.__dict__["roles"] = data.role_names
        return data
```

- [ ] **Step 10: 运行测试，确认全部通过**

```bash
pytest tests/test_auth.py -v
```

Expected: 5 个测试全部 PASSED。

- [ ] **Step 11: 提交**

```bash
git add app/auth/ app/core/deps.py app/main.py tests/conftest.py tests/test_auth.py
git commit -m "feat: 认证模块（注册、登录、JWT、get_current_user）"
```

---

## Task 6: 应用 & 版本模块（TDD）

**Files:**
- Create: `app/application/schemas.py`
- Create: `app/application/service.py`
- Create: `app/application/router.py`
- Modify: `app/main.py`
- Create: `tests/test_applications.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_applications.py`：

```python
import pytest


@pytest.fixture
async def admin_token(client):
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "admin123"
    })
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    return resp.json()["data"]["access_token"]


@pytest.fixture
async def tester_token(client, admin_token):
    await client.post("/api/v1/auth/register", json={
        "username": "tester1", "email": "tester1@test.com", "password": "tester123"
    })
    resp = await client.post("/api/v1/auth/login", json={"username": "tester1", "password": "tester123"})
    return resp.json()["data"]["access_token"]


async def test_create_app_as_admin(client, admin_token):
    resp = await client.post("/api/v1/apps", json={
        "name": "电商平台", "code": "MALL", "description": "主要业务系统"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "电商平台"
    assert data["code"] == "MALL"


async def test_create_app_as_tester_forbidden(client, tester_token):
    resp = await client.post("/api/v1/apps", json={
        "name": "App", "code": "APP"
    }, headers={"Authorization": f"Bearer {tester_token}"})
    assert resp.status_code == 403


async def test_list_apps(client, admin_token):
    await client.post("/api/v1/apps", json={"name": "App1", "code": "A1"},
                      headers={"Authorization": f"Bearer {admin_token}"})
    await client.post("/api/v1/apps", json={"name": "App2", "code": "A2"},
                      headers={"Authorization": f"Bearer {admin_token}"})
    resp = await client.get("/api/v1/apps", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2


async def test_create_version(client, admin_token):
    app_resp = await client.post("/api/v1/apps", json={"name": "MyApp", "code": "MA"},
                                  headers={"Authorization": f"Bearer {admin_token}"})
    app_id = app_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/apps/{app_id}/versions", json={
        "name": "v1.0.0", "description": "首个版本"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "v1.0.0"


async def test_get_app_not_found(client, admin_token):
    resp = await client.get(
        "/api/v1/apps/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 404
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_applications.py -v
```

Expected: 全部 FAILED（路由不存在）。

- [ ] **Step 3: 创建 app/application/schemas.py**

```python
from pydantic import BaseModel
import uuid
from datetime import datetime


class AppCreate(BaseModel):
    name: str
    code: str
    description: str | None = None


class AppUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class AppResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class VersionCreate(BaseModel):
    name: str
    description: str | None = None
    release_date: str | None = None  # ISO date string


class VersionResponse(BaseModel):
    id: uuid.UUID
    app_id: uuid.UUID
    name: str
    description: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
```

- [ ] **Step 4: 创建 app/application/service.py**

```python
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
```

- [ ] **Step 5: 创建 app/application/router.py**

```python
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
```

- [ ] **Step 6: 注册路由到 main.py**

在 `app/main.py` 末尾添加：

```python
from app.application.router import router as app_router
app.include_router(app_router)
```

- [ ] **Step 7: 运行测试，确认全部通过**

```bash
pytest tests/test_applications.py -v
```

Expected: 5 个测试全部 PASSED。

- [ ] **Step 8: 提交**

```bash
git add app/application/ app/main.py tests/test_applications.py
git commit -m "feat: 应用&版本模块（CRUD + 分页 + RBAC）"
```

---

## Task 7: 测试用例模块（TDD）

**Files:**
- Create: `app/test_case/schemas.py`
- Create: `app/test_case/service.py`
- Create: `app/test_case/router.py`
- Modify: `app/main.py`
- Create: `tests/test_test_cases.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_test_cases.py`：

```python
import pytest


@pytest.fixture
async def setup(client):
    """创建 admin 用户、登录、创建应用，返回 (token, app_id)。"""
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "admin123"
    })
    login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["data"]["access_token"]
    app_resp = await client.post("/api/v1/apps", json={"name": "TestApp", "code": "TA"},
                                  headers={"Authorization": f"Bearer {token}"})
    app_id = app_resp.json()["data"]["id"]
    return token, app_id


async def test_create_test_case(client, setup):
    token, app_id = setup
    resp = await client.post(f"/api/v1/apps/{app_id}/test-cases", json={
        "title": "登录-正确账密-成功",
        "priority": "P1",
        "category": "登录模块",
        "steps": [{"step": 1, "action": "输入正确账密", "expected": "登录成功"}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "登录-正确账密-成功"
    assert data["priority"] == "P1"


async def test_list_test_cases_with_filter(client, setup):
    token, app_id = setup
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/apps/{app_id}/test-cases",
                      json={"title": "用例1", "priority": "P0", "category": "登录"},
                      headers=headers)
    await client.post(f"/api/v1/apps/{app_id}/test-cases",
                      json={"title": "用例2", "priority": "P2", "category": "订单"},
                      headers=headers)

    resp = await client.get(f"/api/v1/apps/{app_id}/test-cases?priority=P0", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["items"][0]["title"] == "用例1"


async def test_soft_delete_test_case(client, setup):
    token, app_id = setup
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(f"/api/v1/apps/{app_id}/test-cases",
                                     json={"title": "待删用例"}, headers=headers)
    case_id = create_resp.json()["data"]["id"]

    await client.delete(f"/api/v1/test-cases/{case_id}", headers=headers)

    # 列表里查不到
    list_resp = await client.get(f"/api/v1/apps/{app_id}/test-cases", headers=headers)
    assert list_resp.json()["data"]["total"] == 0

    # 详情返回 404
    get_resp = await client.get(f"/api/v1/test-cases/{case_id}", headers=headers)
    assert get_resp.status_code == 404
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_test_cases.py -v
```

Expected: 全部 FAILED。

- [ ] **Step 3: 创建 app/test_case/schemas.py**

```python
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Any


class TestCaseCreate(BaseModel):
    title: str
    description: str | None = None
    preconditions: str | None = None
    steps: list[dict[str, Any]] | None = None
    expected_result: str | None = None
    category: str | None = None
    priority: str = "P2"
    case_type: str = "functional"
    is_automated: bool = False


class TestCaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    steps: list[dict[str, Any]] | None = None
    expected_result: str | None = None
    category: str | None = None
    priority: str | None = None
    is_automated: bool | None = None


class TestCaseResponse(BaseModel):
    id: uuid.UUID
    app_id: uuid.UUID
    title: str
    description: str | None
    category: str | None
    priority: str
    case_type: str
    is_automated: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: 创建 app/test_case/service.py**

```python
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
```

- [ ] **Step 5: 创建 app/test_case/router.py**

```python
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
```

- [ ] **Step 6: 注册路由到 main.py**

```python
from app.test_case.router import router as test_case_router
app.include_router(test_case_router)
```

- [ ] **Step 7: 运行测试，确认全部通过**

```bash
pytest tests/test_test_cases.py -v
```

Expected: 3 个测试全部 PASSED。

- [ ] **Step 8: 提交**

```bash
git add app/test_case/ app/main.py tests/test_test_cases.py
git commit -m "feat: 测试用例模块（CRUD + 分页过滤 + 软删除）"
```

---

## Task 8: 测试任务 & 执行模块（TDD）

**Files:**
- Create: `app/test_task/schemas.py`
- Create: `app/test_task/service.py`
- Create: `app/test_task/router.py`
- Modify: `app/main.py`
- Create: `tests/test_test_tasks.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_test_tasks.py`：

```python
import pytest
from datetime import datetime, timezone


@pytest.fixture
async def setup(client):
    """创建 admin、登录、建应用、建版本、建用例，返回所需 ID。"""
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "admin123"
    })
    login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    app_resp = await client.post("/api/v1/apps", json={"name": "MyApp", "code": "MA"}, headers=headers)
    app_id = app_resp.json()["data"]["id"]

    ver_resp = await client.post(f"/api/v1/apps/{app_id}/versions",
                                  json={"name": "v1.0"}, headers=headers)
    version_id = ver_resp.json()["data"]["id"]

    case_resp = await client.post(f"/api/v1/apps/{app_id}/test-cases",
                                   json={"title": "用例A"}, headers=headers)
    case_id = case_resp.json()["data"]["id"]

    return token, app_id, version_id, case_id


async def test_create_test_task(client, setup):
    token, app_id, version_id, _ = setup
    resp = await client.post(f"/api/v1/apps/{app_id}/test-tasks", json={
        "name": "第一轮全量测试", "version_id": version_id,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "第一轮全量测试"
    assert resp.json()["data"]["status"] == "pending"


async def test_submit_execution(client, setup):
    token, app_id, version_id, case_id = setup
    headers = {"Authorization": f"Bearer {token}"}

    task_resp = await client.post(f"/api/v1/apps/{app_id}/test-tasks",
                                   json={"name": "任务1", "version_id": version_id}, headers=headers)
    task_id = task_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/test-tasks/{task_id}/executions", json={
        "test_case_id": case_id,
        "result": "fail",
        "actual_result": "页面报错 500",
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["data"]["result"] == "fail"


async def test_list_executions(client, setup):
    token, app_id, version_id, case_id = setup
    headers = {"Authorization": f"Bearer {token}"}

    task_resp = await client.post(f"/api/v1/apps/{app_id}/test-tasks",
                                   json={"name": "任务2", "version_id": version_id}, headers=headers)
    task_id = task_resp.json()["data"]["id"]

    await client.post(f"/api/v1/test-tasks/{task_id}/executions", json={
        "test_case_id": case_id, "result": "pass",
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }, headers=headers)

    resp = await client.get(f"/api/v1/test-tasks/{task_id}/executions", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_test_tasks.py -v
```

Expected: 全部 FAILED。

- [ ] **Step 3: 创建 app/test_task/schemas.py**

```python
from pydantic import BaseModel
import uuid
from datetime import datetime, date


class TestTaskCreate(BaseModel):
    name: str
    version_id: uuid.UUID
    description: str | None = None
    assignee_id: uuid.UUID | None = None
    start_date: date | None = None
    due_date: date | None = None


class TestTaskResponse(BaseModel):
    id: uuid.UUID
    app_id: uuid.UUID
    version_id: uuid.UUID
    name: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExecutionCreate(BaseModel):
    test_case_id: uuid.UUID
    result: str
    actual_result: str | None = None
    executed_at: datetime
    duration_seconds: int | None = None


class ExecutionResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    test_case_id: uuid.UUID
    result: str
    actual_result: str | None
    executed_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: 创建 app/test_task/service.py**

```python
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
```

- [ ] **Step 5: 创建 app/test_task/router.py**

```python
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import success, created
from app.core.deps import get_current_user, require_roles
from app.test_task import service
from app.test_task.schemas import (
    TestTaskCreate, TestTaskResponse, ExecutionCreate, ExecutionResponse
)
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["测试任务"])


@router.post("/apps/{app_id}/test-tasks")
def create_task(
    app_id: uuid.UUID,
    payload: TestTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    task = service.create_test_task(db, app_id, payload.model_dump(exclude_none=True), current_user.id)
    return created(TestTaskResponse.model_validate(task).model_dump(mode="json"))


@router.get("/apps/{app_id}/test-tasks")
def list_tasks(
    app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = service.list_test_tasks(db, app_id)
    return success([TestTaskResponse.model_validate(t).model_dump(mode="json") for t in tasks])


@router.get("/test-tasks/{task_id}")
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = service.get_test_task(db, task_id)
    return success(TestTaskResponse.model_validate(task).model_dump(mode="json"))


@router.post("/test-tasks/{task_id}/executions")
def create_execution(
    task_id: uuid.UUID,
    payload: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "tester")),
):
    execution = service.create_execution(
        db, task_id, payload.model_dump(exclude_none=True), current_user.id
    )
    return created(ExecutionResponse.model_validate(execution).model_dump(mode="json"))


@router.get("/test-tasks/{task_id}/executions")
def list_executions(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    executions = service.list_executions(db, task_id)
    return success([ExecutionResponse.model_validate(e).model_dump(mode="json") for e in executions])
```

- [ ] **Step 6: 注册路由到 main.py**

```python
from app.test_task.router import router as test_task_router
app.include_router(test_task_router)
```

- [ ] **Step 7: 运行测试**

```bash
pytest tests/test_test_tasks.py -v
```

Expected: 3 个测试全部 PASSED。

- [ ] **Step 8: 提交**

```bash
git add app/test_task/ app/main.py tests/test_test_tasks.py
git commit -m "feat: 测试任务&执行模块"
```

---

## Task 9: 缺陷状态机（先写单元测试）

**Files:**
- Create: `app/defect/state_machine.py`
- Create: `tests/test_state_machine.py`

- [ ] **Step 1: 写失败的状态机单元测试**

创建 `tests/test_state_machine.py`：

```python
import pytest
from app.defect.state_machine import validate_transition
from app.core.exceptions import BusinessError


# ── 合法流转 ──────────────────────────────────────────
def test_new_to_assigned_by_tester():
    validate_transition("new", "assigned", ["tester"])  # 不抛异常即通过


def test_assigned_to_fixed_by_developer():
    validate_transition("assigned", "fixed", ["developer"])


def test_fixed_to_verified_by_tester():
    validate_transition("fixed", "verified", ["tester"])


def test_verified_to_closed_by_admin():
    validate_transition("verified", "closed", ["admin"])


def test_closed_to_reopened_by_admin():
    validate_transition("closed", "reopened", ["admin"])


def test_reopened_to_assigned_by_tester():
    validate_transition("reopened", "assigned", ["tester"])


def test_assigned_to_rejected_by_tester():
    validate_transition("assigned", "rejected", ["tester"])


def test_fixed_to_reopened_by_tester():
    validate_transition("fixed", "reopened", ["tester"])


# ── 非法状态跳转 ──────────────────────────────────────
def test_invalid_new_to_fixed():
    with pytest.raises(BusinessError) as exc:
        validate_transition("new", "fixed", ["tester"])
    assert exc.value.code == "INVALID_TRANSITION"


def test_invalid_new_to_closed():
    with pytest.raises(BusinessError) as exc:
        validate_transition("new", "closed", ["admin"])
    assert exc.value.code == "INVALID_TRANSITION"


def test_invalid_verified_to_assigned():
    with pytest.raises(BusinessError) as exc:
        validate_transition("verified", "assigned", ["admin"])
    assert exc.value.code == "INVALID_TRANSITION"


def test_rejected_is_terminal():
    with pytest.raises(BusinessError) as exc:
        validate_transition("rejected", "assigned", ["admin"])
    assert exc.value.code == "INVALID_TRANSITION"


# ── 权限不足 ──────────────────────────────────────────
def test_developer_cannot_close():
    with pytest.raises(BusinessError) as exc:
        validate_transition("verified", "closed", ["developer"])
    assert exc.value.code == "TRANSITION_FORBIDDEN"


def test_developer_cannot_assign():
    with pytest.raises(BusinessError) as exc:
        validate_transition("new", "assigned", ["developer"])
    assert exc.value.code == "TRANSITION_FORBIDDEN"


def test_readonly_cannot_do_anything():
    with pytest.raises(BusinessError):
        validate_transition("new", "assigned", ["readonly"])


def test_multi_role_allows_if_any_matches():
    # 用户同时有 developer 和 tester 角色，tester 能做这个操作
    validate_transition("new", "assigned", ["developer", "tester"])
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_state_machine.py -v
```

Expected: 全部 FAILED（模块不存在）。

- [ ] **Step 3: 创建 app/defect/state_machine.py**

```python
from app.core.exceptions import BusinessError

# 允许的状态流转：{当前状态: [可到达的状态列表]}
VALID_TRANSITIONS: dict[str, list[str]] = {
    "new":      ["assigned"],
    "assigned": ["fixed", "rejected"],
    "fixed":    ["verified", "reopened"],
    "verified": ["closed"],
    "rejected": [],            # 终态，不能再流转
    "closed":   ["reopened"],
    "reopened": ["assigned"],
}

# 每条流转允许的角色：{(from, to): [角色列表]}
ROLE_PERMISSIONS: dict[tuple[str, str], list[str]] = {
    ("new",      "assigned"): ["admin", "tester"],
    ("assigned", "fixed"):    ["developer"],
    ("assigned", "rejected"): ["admin", "tester"],
    ("fixed",    "verified"): ["tester"],
    ("fixed",    "reopened"): ["tester"],
    ("verified", "closed"):   ["admin", "tester"],
    ("closed",   "reopened"): ["admin"],
    ("reopened", "assigned"): ["admin", "tester"],
}


def validate_transition(from_status: str, to_status: str, user_roles: list[str]) -> None:
    """
    验证缺陷状态流转是否合法。
    - 状态跳转不合法：抛 BusinessError(code="INVALID_TRANSITION")
    - 角色无权执行：抛 BusinessError(code="TRANSITION_FORBIDDEN")
    """
    allowed_targets = VALID_TRANSITIONS.get(from_status, [])
    if to_status not in allowed_targets:
        raise BusinessError(
            code="INVALID_TRANSITION",
            message=f"无效的状态流转：{from_status} → {to_status}",
        )

    allowed_roles = ROLE_PERMISSIONS.get((from_status, to_status), [])
    if not any(role in allowed_roles for role in user_roles):
        raise BusinessError(
            code="TRANSITION_FORBIDDEN",
            message=f"当前角色无权执行此状态流转",
        )
```

- [ ] **Step 4: 运行测试，确认全部通过**

```bash
pytest tests/test_state_machine.py -v
```

Expected: 16 个测试全部 PASSED。

- [ ] **Step 5: 提交**

```bash
git add app/defect/state_machine.py tests/test_state_machine.py
git commit -m "feat: 缺陷状态机（含完整单元测试覆盖）"
```

---

## Task 10: 缺陷模块（TDD）

**Files:**
- Create: `app/defect/schemas.py`
- Create: `app/defect/service.py`
- Create: `app/defect/router.py`
- Modify: `app/main.py`
- Create: `tests/test_defects.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_defects.py`：

```python
import pytest
from datetime import datetime, timezone


@pytest.fixture
async def setup(client):
    """注册 admin/developer/tester，建好应用+版本，返回 tokens 和 IDs。"""
    # admin（第一个注册的用户）
    await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin@t.com", "password": "admin123"
    })
    login_a = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = login_a.json()["data"]["access_token"]
    ah = {"Authorization": f"Bearer {admin_token}"}

    # 建应用和版本
    app_resp = await client.post("/api/v1/apps", json={"name": "App", "code": "APP"}, headers=ah)
    app_id = app_resp.json()["data"]["id"]
    ver_resp = await client.post(f"/api/v1/apps/{app_id}/versions",
                                  json={"name": "v1.0"}, headers=ah)
    version_id = ver_resp.json()["data"]["id"]

    # developer 用户（admin 手动改角色，或直接用 admin 创建）
    await client.post("/api/v1/auth/register", json={
        "username": "dev1", "email": "dev1@t.com", "password": "dev123"
    })
    login_d = await client.post("/api/v1/auth/login", json={"username": "dev1", "password": "dev123"})
    dev_token = login_d.json()["data"]["access_token"]

    return admin_token, dev_token, app_id, version_id


async def test_create_defect(client, setup):
    admin_token, _, app_id, version_id = setup
    resp = await client.post(f"/api/v1/apps/{app_id}/defects", json={
        "title": "登录页报错",
        "severity": "high",
        "priority": "P1",
        "found_version_id": version_id,
        "steps_to_reproduce": "1.打开登录页 2.点登录",
        "actual_result": "500 Internal Server Error",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "登录页报错"
    assert data["status"] == "new"
    assert data["defect_no"].startswith("APP-")


async def test_defect_no_auto_increment(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    r1 = await client.post(f"/api/v1/apps/{app_id}/defects",
                            json={"title": "Bug1", "found_version_id": version_id}, headers=headers)
    r2 = await client.post(f"/api/v1/apps/{app_id}/defects",
                            json={"title": "Bug2", "found_version_id": version_id}, headers=headers)
    no1 = r1.json()["data"]["defect_no"]
    no2 = r2.json()["data"]["defect_no"]
    assert no1 != no2
    assert no1 == "APP-0001"
    assert no2 == "APP-0002"


async def test_transition_new_to_assigned(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/defects/{defect_id}/transitions", json={
        "to_status": "assigned", "comment": "指派处理"
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "assigned"


async def test_invalid_transition_raises_400(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    # new → closed 是非法跳转
    resp = await client.post(f"/api/v1/defects/{defect_id}/transitions",
                              json={"to_status": "closed"}, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TRANSITION"


async def test_add_and_list_comments(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    await client.post(f"/api/v1/defects/{defect_id}/comments",
                      json={"content": "已确认，指派开发"}, headers=headers)

    detail = await client.get(f"/api/v1/defects/{defect_id}", headers=headers)
    assert len(detail.json()["data"]["comments"]) == 1
    assert detail.json()["data"]["comments"][0]["content"] == "已确认，指派开发"


async def test_defect_status_history_recorded(client, setup):
    admin_token, _, app_id, version_id = setup
    headers = {"Authorization": f"Bearer {admin_token}"}
    defect_resp = await client.post(f"/api/v1/apps/{app_id}/defects",
                                     json={"title": "Bug", "found_version_id": version_id},
                                     headers=headers)
    defect_id = defect_resp.json()["data"]["id"]

    await client.post(f"/api/v1/defects/{defect_id}/transitions",
                      json={"to_status": "assigned"}, headers=headers)

    history_resp = await client.get(f"/api/v1/defects/{defect_id}/history", headers=headers)
    history = history_resp.json()["data"]
    assert len(history) == 1
    assert history[0]["from_status"] == "new"
    assert history[0]["to_status"] == "assigned"
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_defects.py -v
```

Expected: 全部 FAILED。

- [ ] **Step 3: 创建 app/defect/schemas.py**

```python
from pydantic import BaseModel
import uuid
from datetime import datetime


class DefectCreate(BaseModel):
    title: str
    description: str | None = None
    steps_to_reproduce: str | None = None
    expected_result: str | None = None
    actual_result: str | None = None
    severity: str = "medium"
    priority: str = "P2"
    found_version_id: uuid.UUID
    fix_version_id: uuid.UUID | None = None
    assignee_id: uuid.UUID | None = None
    source: str = "manual"


class DefectTransition(BaseModel):
    to_status: str
    assignee_id: uuid.UUID | None = None
    comment: str | None = None


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StatusHistoryResponse(BaseModel):
    id: uuid.UUID
    from_status: str | None
    to_status: str
    changed_by: uuid.UUID
    comment: str | None
    changed_at: datetime

    model_config = {"from_attributes": True}


class DefectResponse(BaseModel):
    id: uuid.UUID
    defect_no: str
    app_id: uuid.UUID
    title: str
    severity: str
    priority: str
    status: str
    source: str
    reporter_id: uuid.UUID
    assignee_id: uuid.UUID | None
    found_version_id: uuid.UUID
    fix_version_id: uuid.UUID | None
    created_at: datetime
    comments: list[CommentResponse] = []

    model_config = {"from_attributes": True}


class DefectListResponse(BaseModel):
    id: uuid.UUID
    defect_no: str
    title: str
    severity: str
    priority: str
    status: str
    reporter_id: uuid.UUID
    assignee_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: 创建 app/defect/service.py**

```python
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.defect import Defect, DefectComment, DefectStatusHistory
from app.models.application import Application
from app.core.exceptions import NotFoundError, BusinessError
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
```

- [ ] **Step 5: 创建 app/defect/router.py**

```python
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
```

- [ ] **Step 6: 注册路由到 main.py**

```python
from app.defect.router import router as defect_router
app.include_router(defect_router)
```

- [ ] **Step 7: 运行全部测试**

```bash
pytest tests/ -v
```

Expected: 全部 PASSED（auth、applications、test_cases、test_tasks、state_machine、defects）。

- [ ] **Step 8: 提交**

```bash
git add app/defect/ app/main.py tests/test_defects.py
git commit -m "feat: 缺陷模块（状态机、评论、历史记录）"
```

---

## Task 11: Docker 配置

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 创建 docker-compose.yml**

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/test_center
      SECRET_KEY: docker-dev-secret-key-change-in-production
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
    volumes:
      - .:/app  # 开发模式：代码变更自动生效

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test_center
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    # Phase 1 占位，Phase 2 Week 3 正式使用

volumes:
  postgres_data:
```

- [ ] **Step 3: 添加 .dockerignore**

```
venv/
__pycache__/
*.pyc
.env
.git/
tests/
*.md
```

- [ ] **Step 4: 启动并执行迁移**

```bash
docker compose up -d --build
# 等待服务启动后执行迁移
docker compose exec api alembic upgrade head
```

Expected: 
- `docker compose ps` 显示 api 和 db 均为 `running`
- 迁移成功输出 `Running upgrade -> xxxx`

- [ ] **Step 5: 验证 API 可用**

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}

curl http://localhost:8000/docs
# 浏览器访问 http://localhost:8000/docs，看到完整 Swagger UI
```

- [ ] **Step 6: 提交最终版本**

```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "feat: Docker 容器化（FastAPI + PostgreSQL + Redis）"
```

---

## 验收检查清单

全部完成后，运行以下命令验证 Phase 1 交付物：

```bash
# 1. 全量测试通过
pytest tests/ -v --tb=short

# 2. 启动服务验证接口文档完整
uvicorn app.main:app --reload
# 访问 http://localhost:8000/docs，确认所有接口都在

# 3. Docker 启动验证
docker compose up -d
docker compose exec api alembic upgrade head
curl http://localhost:8000/health
```

**Phase 1 交付物：**
- [x] FastAPI 生产级 REST API（含认证、数据库、统一响应、全局异常）
- [x] 12 张表完整建模 + Alembic 迁移
- [x] JWT 认证 + RBAC（admin/tester/developer/readonly）
- [x] 核心流程可跑通（应用→版本→用例→任务→执行→缺陷→状态流转）
- [x] 缺陷状态机（8 条合法路径 + 权限矩阵）
- [x] pytest 测试覆盖（auth、application、test_case、test_task、state_machine、defect）
- [x] Docker Compose（FastAPI + PostgreSQL + Redis）
