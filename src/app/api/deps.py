from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.pagination import PaginationParams

DatabaseSession = Annotated[Session, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends()]

__all__ = ["DatabaseSession", "PaginationDep", "get_db"]


