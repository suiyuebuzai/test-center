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
