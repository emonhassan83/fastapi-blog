from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.user.models import User
from app.modules.user.repository import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user by email and password."""
        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def login(self, login_data: LoginRequest) -> TokenResponse:
        """Authenticate and issue a signed JWT access token."""
        user = self.authenticate_user(login_data.email, login_data.password)
        expires_minutes = settings.jwt_access_token_expire_minutes
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            expires_delta=timedelta(minutes=expires_minutes),
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_minutes * 60,
        )
