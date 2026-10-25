from sqlalchemy.orm import Session

from app.modules.auth.repository import AuthRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.repository = AuthRepository(session)
