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

class Project(Base):
    __tablename__ = "projects"
    
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    project_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[ProjectStatusEnum] = mapped_column(
        SAEnum(ProjectStatusEnum, name="projectstatus", values_callable=lambda x: [e.value for e in x]), 
        default=ProjectStatusEnum.DRAFT
    )
    
    # Integration Fields
    source: Mapped[ProjectSourceEnum] = mapped_column(
        SAEnum(ProjectSourceEnum, name="projectsource", values_callable=lambda x: [e.value for e in x]), 
        default=ProjectSourceEnum.NATIVE, server_default="native"
    ) 
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    # Project Charter & Content - MOVED TO PROPERTIES TABLEtructured)
    # Relationship to Properties (Polymorphic-like)
    properties_rel: Mapped["Property"] = relationship(
        "Property",
        primaryjoin="and_(foreign(Property.entity_id) == Project.project_id, "
                    "Property.entity_type == 'project')",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @property
    def properties(self) -> dict:
        return self.properties_rel.data if self.properties_rel else {}

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