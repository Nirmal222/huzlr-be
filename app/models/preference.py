from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger, JSON, ForeignKey, UniqueConstraint
from models.base import Base

class PropertyPreference(Base):
    __tablename__ = "property_preferences"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    preferences: Mapped[dict] = mapped_column(JSON, default=lambda: {})

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="property_preferences")

    __table_args__ = (
        UniqueConstraint('user_id', 'entity_type', name='uq_user_entity_preference'),
    )
