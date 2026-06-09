import uuid
from sqlalchemy import String, Boolean, Text, ForeignKey
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
