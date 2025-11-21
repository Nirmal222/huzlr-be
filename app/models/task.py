from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text
from models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Date, Boolean

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # NEW: Fields for project management
    milestone_id: Mapped[int | None] = mapped_column(ForeignKey("milestones.milestone_id"), nullable=True)
    scenario_id: Mapped[int | None] = mapped_column(ForeignKey("scenarios.scenario_id"), nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    critical_path_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Add these relationships
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="tasks")
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="tasks")
    dependencies: Mapped[list["TaskDependency"]] = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan"
    )