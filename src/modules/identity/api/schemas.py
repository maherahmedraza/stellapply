import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    name: str = Field(..., min_length=1, description="User's full name")
    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )


class UserResponse(UserBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    governance_metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str = "Bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
