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
