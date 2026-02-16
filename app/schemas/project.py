from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from typing import Optional, Any, Dict

from core.property_factory import create_pydantic_model_from_schema

# Auto-generate properties model from registry (Unified - includes ALL fields)
UnifiedProjectProperties = create_pydantic_model_from_schema("project")

class ProjectStats(BaseModel):
    scope: Optional[int] = None
    completed: Optional[int] = None
    progress: Optional[int] = None
    target: Optional[str] = None
    limit: Optional[str] = None

class ProjectBase(BaseModel):
    # This is still useful for internal typing but we are decoupling API from it
    pass

class ProjectCreate(BaseModel):
    user_id: int
    properties: UnifiedProjectProperties
    lead_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    properties: Optional[UnifiedProjectProperties] = None
    lead_id: Optional[int] = None

class ProjectResponse(BaseModel):
    project_id: int
    user_id: int
    properties: UnifiedProjectProperties
    lead_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
