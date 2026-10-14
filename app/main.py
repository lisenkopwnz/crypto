from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.prices import create_router
from app.config import Settings
from app.db.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.database = Database(settings.database_url)
        yield
        await app.state.database.dispose()

    app = FastAPI(title="Deribit prices API", lifespan=lifespan)
    app.include_router(create_router(), prefix="/api/v1")
    return app
