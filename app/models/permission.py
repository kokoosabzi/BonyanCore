from sqlalchemy import Column, String, Boolean, Text
from app.models.base import BaseModel

class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    module = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)