from fastapi import APIRouter

from app.api.deps import DatabaseSession  # noqa: F401
from app.modules.auth.service import AuthService  # noqa: F401

router = APIRouter()
