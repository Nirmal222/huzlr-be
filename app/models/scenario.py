from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, Date, ForeignKey
from datetime import datetime, date
from models.base import Base

class Scenario(Base):
    __tablename__ = "scenarios"
    
    scenario_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(20))  # optimistic, realistic, pessimistic
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    estimated_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scenarios")
    milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="scenario", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="scenario")


class Milestone(Base):
    __tablename__ = "milestones"
    
    milestone_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(Integer, ForeignKey("scenarios.scenario_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    order_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    # Relationships
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="milestones")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="milestone")