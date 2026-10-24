import uvicorn
from fastapi import FastAPI

from app.api.v1 import router as api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router)
    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
