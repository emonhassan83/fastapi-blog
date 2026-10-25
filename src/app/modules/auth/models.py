from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Auth(Base):
    __tablename__ = "auths"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
