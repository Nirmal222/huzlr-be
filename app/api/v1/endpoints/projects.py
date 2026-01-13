from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.project import Project
from models.property import Property, EntityTypeEnum
from models.user import User
from schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    return projects

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Prepare data excluding properties (handled via relationship) and overriding user_id
    project_data = project.model_dump(exclude={'properties', 'user_id'})
    project_data['user_id'] = current_user.id
    
    db_project = Project(**project_data)
    
    # Handle properties automatically via the relationship
    if project.properties:
        db_project.properties_rel = Property(
            entity_type=EntityTypeEnum.PROJECT, 
            data=project.properties
        )
            
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalars().first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check authorization
    if project.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized to access this project")

    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int, 
    project_update: ProjectUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    db_project = result.scalars().first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if db_project.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized to update this project")
    
    update_data = project_update.model_dump(exclude_unset=True, exclude={'properties'})
    
    # Update regular fields
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    # Update properties if present
    if project_update.properties is not None:
        if db_project.properties_rel:
            # Update existing property record
            # We need to assign a new dict to ensure SQLAlchemy tracks the change for JSON fields
            # Or use flag_modified, but reassignment is safer
            db_project.properties_rel.data = project_update.properties
        else:
            # Create new property record if it didn't exist
            db_project.properties_rel = Property(
                entity_type=EntityTypeEnum.PROJECT, 
                data=project_update.properties
            )
        
    await db.commit()
    await db.refresh(db_project)
    return db_project
