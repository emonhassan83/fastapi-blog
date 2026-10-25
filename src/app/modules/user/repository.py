from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.user.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_by_username(self, username: str) -> User | None:
        return self.session.scalar(select(User).where(User.username == username))

    def create(self, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username,
            email=email,
            password=hashed_password,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
