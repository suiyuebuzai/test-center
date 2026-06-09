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
