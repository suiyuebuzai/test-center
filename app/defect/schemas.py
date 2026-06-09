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
