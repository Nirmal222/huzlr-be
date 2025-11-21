from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from models.base import Base

class Risk(Base):
    __tablename__ = "risks"
    
    risk_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    likelihood: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    impact: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    mitigation_strategy: Mapped[str | None] = mapped_column(Text(), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="risks")


class Assumption(Base):
    __tablename__ = "assumptions"
    
    assumption_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="assumptions")