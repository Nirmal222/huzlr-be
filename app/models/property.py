from sqlalchemy import Integer, String, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from models.base import Base

class EntityTypeEnum(str, enum.Enum):
    PROJECT = "project"
    ISSUE = "issue"

class Property(Base):
    __tablename__ = "properties"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[EntityTypeEnum] = mapped_column(
        SAEnum(EntityTypeEnum, name="entitytype", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    entity_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
