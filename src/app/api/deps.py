from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.user.models import User
from app.modules.user.repository import UserRepository
from app.shared.pagination import PaginationParams

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DatabaseSession = Annotated[Session, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends()]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DatabaseSession,
) -> User:
    """Validate JWT token and resolve current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc

    raw_user_id = payload.get("user_id") or payload.get("sub")
    if raw_user_id is None:
        raise credentials_exception

    try:
        user_id = int(raw_user_id)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

__all__ = [
    "CurrentUser",
    "DatabaseSession",
    "PaginationDep",
    "get_current_user",
    "get_db",
    "oauth2_scheme",
]
