from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.milestone import Milestone
from models.project import Project
from schemas.milestone import MilestoneResponse, MilestoneCreate, MilestoneUpdate
from models.user import User
from api.deps import get_current_user

router = APIRouter()

@router.get("/projects/{project_id}/milestones", response_model=list[MilestoneResponse])
async def list_project_milestones(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify project exists and user has access
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.order_index)
    )
    milestones = result.scalars().all()
    return milestones

@router.post("/projects/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_project_milestone(
    project_id: int,
    milestone: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if milestone.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID in path does not match payload")

    # Verify project exists and user has access
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_milestone = Milestone(**milestone.model_dump())
    db.add(db_milestone)
    await db.commit()
    await db.refresh(db_milestone)
    return db_milestone

@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    milestone_update: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Milestone).where(Milestone.milestone_id == milestone_id))
    db_milestone = result.scalars().first()
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    # Verify user owns the project this milestone belongs to
    result = await db.execute(select(Project).where(Project.project_id == db_milestone.project_id))
    project = result.scalars().first()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = milestone_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_milestone, key, value)

    await db.commit()
    await db.refresh(db_milestone)
    return db_milestone

@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Milestone).where(Milestone.milestone_id == milestone_id))
    db_milestone = result.scalars().first()
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    # Verify user owns the project
    result = await db.execute(select(Project).where(Project.project_id == db_milestone.project_id))
    project = result.scalars().first()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(db_milestone)
    await db.commit()
    return None
