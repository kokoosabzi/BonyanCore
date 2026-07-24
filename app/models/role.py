from sqlalchemy import Column, String, Boolean, Text
from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    permissions = Column(Text, nullable=True)  # JSON or comma-separated