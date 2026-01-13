from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from models.project import ProjectStatusEnum, ProjectSourceEnum, ProjectPriorityEnum

class ProjectStats(BaseModel):
    scope: Optional[int] = None
    completed: Optional[int] = None
    progress: Optional[int] = None
    target: Optional[str] = None
    limit: Optional[str] = None

class ProjectProperties(BaseModel):
    # Charter & Content
    purpose: Optional[dict | list | str] = None
    objectives: Optional[list] = None
    deliverables: Optional[list] = None
    scope: Optional[dict | str] = None
    timeline: Optional[dict | str] = None
    budget: Optional[dict | str] = None
    stakeholders: Optional[list | str] = None
    team_members: Optional[list | str] = None
    resources: Optional[list] = None
    milestones: Optional[list] = None
    integration_metadata: Optional[dict] = None
    
    # Metadata
    priority: Optional[ProjectPriorityEnum] = None
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    labels: Optional[list] = None
    teams: Optional[list] = None
    stats: Optional[ProjectStats] = None
    
    # UI Specific
    type: Optional[str] = None
    reviewer: Optional[str] = None

    model_config = ConfigDict(extra='allow') # Allow future extensibility via simple dict if needed

class ProjectBase(BaseModel):
    project_title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = ProjectStatusEnum.DRAFT
    
    # Integration Fields
    source: Optional[ProjectSourceEnum] = ProjectSourceEnum.NATIVE
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    
    # Consolidated Properties
    properties: Optional[ProjectProperties] = None
    
    lead_id: Optional[int] = None

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
