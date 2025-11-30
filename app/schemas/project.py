from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    project_title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "draft"

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
