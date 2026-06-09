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
