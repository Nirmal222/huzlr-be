from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.task import Task


router = APIRouter()


@router.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(Task.__table__.select())
    return result.fetchall()