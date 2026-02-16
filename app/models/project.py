from sqlalchemy import String, Integer, BigInteger, Text, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models.base import Base
import enum

class ProjectStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    BACKLOG = "backlog"

class ProjectSourceEnum(str, enum.Enum):
    NATIVE = "native"
    JIRA = "jira"
    LINEAR = "linear"
    GITHUB = "github"

class ProjectPriorityEnum(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class ProjectHealthEnum(str, enum.Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OFF_TRACK = "off_track"

class Project(Base):
    __tablename__ = "projects"
    
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # Unified Properties Column (JSONB)
    # Stores all domain fields: title, status, description, etc.
    properties: Mapped[dict] = mapped_column(JSON, default={}, server_default='{}')

    # Linear-style Metadata
    lead_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)



    # Linear-style Metadata
    lead_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="projects")
    lead: Mapped["User"] = relationship("User", foreign_keys=[lead_id])
    
    inputs: Mapped[list["ProjectInput"]] = relationship("ProjectInput", back_populates="project", cascade="all, delete-orphan")
    # intents relationship removed as part of consolidation
    scenarios: Mapped[list["Scenario"]] = relationship("Scenario", back_populates="project", cascade="all, delete-orphan")
    risks: Mapped[list["Risk"]] = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    assumptions: Mapped[list["Assumption"]] = relationship("Assumption", back_populates="project", cascade="all, delete-orphan")
    conversation_logs: Mapped[list["ConversationLog"]] = relationship("ConversationLog", back_populates="project", cascade="all, delete-orphan")
    versions: Mapped[list["ProjectVersion"]] = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")
    

class ProjectInput(Base):
    __tablename__ = "project_inputs"
    
    input_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    raw_audio_path: Mapped[str | None] = mapped_column(Text(), nullable=True)
    raw_transcript: Mapped[str | None] = mapped_column(Text(), nullable=True)
    cleaned_transcript: Mapped[str | None] = mapped_column(Text(), nullable=True)
    final_prompt: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    


    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="inputs")