from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from datetime import datetime
from models.base import Base

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    speaker: Mapped[str | None] = mapped_column(String(20), nullable=True)  # user, huzlr
    audio_path: Mapped[str | None] = mapped_column(Text(), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text(), nullable=True)
    message_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # question, confirmation, revision, system
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="conversation_logs")