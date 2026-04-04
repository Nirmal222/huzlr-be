from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base

class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default={}, server_default='{}')

    # Add indices for fast lookup
    # We query properties by entity_type and entity_id often
    __table_args__ = (
        {"schema": "public"} if False else ()
    )
