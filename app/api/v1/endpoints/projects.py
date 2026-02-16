from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.project import Project
from models.project import Project
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
    # Direct mapping: properties are already in the correct structure for the JSONB column
    # We dump the model, explicitly converting properties to dict
    project_data = project.model_dump()
    project_data['user_id'] = current_user.id
    
    # Ensure properties is a dict for JSONB
    if 'properties' in project_data and hasattr(project_data['properties'], 'model_dump'):
         project_data['properties'] = project_data['properties'].model_dump()
    
    db_project = Project(**project_data)
            
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
    
    update_data = project_update.model_dump(exclude_unset=True)
    
    if 'properties' in update_data:
        # Merge new properties with existing ones
        existing_props = dict(db_project.properties) if db_project.properties else {}
        new_props = update_data['properties']
        
        # If it's a model, dump it
        if hasattr(new_props, 'model_dump'):
            new_props = new_props.model_dump(exclude_unset=True)
            
        existing_props.update(new_props)
        # Reassign to trigger update
        db_project.properties = existing_props
        
        # Remove properties from update_data to avoid double assignment if we iterate
        del update_data['properties']

    # Update other fields (like lead_id)
    for key, value in update_data.items():
        setattr(db_project, key, value)
        
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalars().first()
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized to delete this project")
         
    await db.delete(project)
    await db.commit()
    return None

@router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_projects(
    project_ids: list[int] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all projects to be deleted to ensure ownership and existence
    result = await db.execute(
        select(Project)
        .where(Project.project_id.in_(project_ids))
        .where(Project.user_id == current_user.id)
    )
    projects = result.scalars().all()
    
    for project in projects:
        await db.delete(project)
    
    await db.commit()
    return None
