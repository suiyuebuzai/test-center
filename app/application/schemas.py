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
