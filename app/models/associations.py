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
