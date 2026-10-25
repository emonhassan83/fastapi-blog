from sqlalchemy.orm import Session

from app.modules.auth.models import Auth  # noqa: F401


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
