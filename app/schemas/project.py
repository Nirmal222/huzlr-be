from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    project_title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "draft"
    
    # Charter Fields
    purpose: Optional[str] = None
    objectives: Optional[str] = None
    scope: Optional[str] = None
    deliverables: Optional[str] = None
    timeline: Optional[str] = None
    budget: Optional[str] = None
    stakeholders: Optional[str] = None
    team_members: Optional[str] = None

class ProjectCreate(ProjectBase):
    user_id: int
    project_title: str  # Making title required for creation

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
