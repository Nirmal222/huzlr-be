from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: Optional[int] = None
    estimated_start_date: Optional[date] = None
    estimated_end_date: Optional[date] = None

class MilestoneCreate(MilestoneBase):
    project_id: int

class MilestoneUpdate(MilestoneBase):
    title: Optional[str] = None

class MilestoneResponse(MilestoneBase):
    milestone_id: int
    project_id: int
    
    model_config = ConfigDict(from_attributes=True)
