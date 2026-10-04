from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router
from .database.database import initialize_database


@asynccontextmanager
async def lifespan(app):
    initialize_database()
    yield


app = FastAPI(title="Calculator API", lifespan=lifespan)
app.include_router(router)
