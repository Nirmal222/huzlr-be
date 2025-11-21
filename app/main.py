from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router
from models.task import Base
from core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(router)
