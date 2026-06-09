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
