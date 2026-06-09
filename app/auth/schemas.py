from pydantic import BaseModel, EmailStr, model_validator
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

    @model_validator(mode="before")
    @classmethod
    def extract_roles(cls, data):
        if hasattr(data, "role_names"):
            data.__dict__["roles"] = data.role_names
        return data


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
