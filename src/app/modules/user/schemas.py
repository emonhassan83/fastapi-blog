from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(
        ..., min_length=6, max_length=100, description="Plain text password"
    )


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    message: str
    data: UserRead
