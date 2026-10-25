from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.shared.pagination import PaginationMeta


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


class PostUpdate(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    rating: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    message: str
    data: PostRead


class PostListResponse(BaseModel):

    message: str
    data: list[PostRead]
    pagination: PaginationMeta

