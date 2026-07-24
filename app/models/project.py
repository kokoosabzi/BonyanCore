from sqlalchemy import Column, String, Date, Boolean, Text, Integer
from app.models.base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"

    project_code = Column(String(2), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String(20), default="ACTIVE")
    total_units = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)