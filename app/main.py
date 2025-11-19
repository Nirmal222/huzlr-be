from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.models.task import Base
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(router)
