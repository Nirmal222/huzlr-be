from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger, Text, Float, ForeignKey
from datetime import datetime
from models.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    project_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, completed, archived
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    inputs: Mapped[list["ProjectInput"]] = relationship("ProjectInput", back_populates="project", cascade="all, delete-orphan")
    intents: Mapped[list["ProjectIntent"]] = relationship("ProjectIntent", back_populates="project", cascade="all, delete-orphan")
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


class ProjectIntent(Base):
    __tablename__ = "project_intents"
    
    intent_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    scope: Mapped[str | None] = mapped_column(Text(), nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text(), nullable=True)
    deliverables: Mapped[str | None] = mapped_column(Text(), nullable=True)
    timeline_hints: Mapped[str | None] = mapped_column(Text(), nullable=True)
    extracted_goals: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="intents")