from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.user.models import User
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import UserRegister


class UserService:
    def __init__(self, session: Session) -> None:
        self.repository = UserRepository(session)

    def register_user(self, user_data: UserRegister) -> User:
        if self.repository.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        if self.repository.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken",
            )

        hashed_pwd = hash_password(user_data.password)
        return self.repository.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pwd,
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)
