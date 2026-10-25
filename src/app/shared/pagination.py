from math import ceil
from typing import Annotated, Self

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams:
    """Dependency class to parse and validate pagination query parameters."""

    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Number of items per page (max 100)")
        ] = 10,
    ) -> None:
        self.page = page
        self.limit = limit

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    """Metadata describing the pagination state."""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page limit")
    total_pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(cls, total: int, page: int, limit: int) -> Self:
        total_pages = ceil(total / limit) if total > 0 else 0
        return cls(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )


class PaginatedResponse[DataT](BaseModel):
    """Standard generic wrapper envelope for paginated endpoints."""

    message: str
    data: list[DataT]
    pagination: PaginationMeta
