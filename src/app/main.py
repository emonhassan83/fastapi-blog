import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.database import Base, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            logger.exception("PostgreSQL connection failed; server startup aborted.")
            raise RuntimeError(
                "PostgreSQL database is unavailable; server startup aborted."
            ) from exc

        logger.info("PostgreSQL connection established successfully.")
        print("PostgreSQL connection established successfully.")
        Base.metadata.create_all(bind=engine)
        yield
    finally:
        engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {"message": "Hello from fastapi-blog!"}

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
