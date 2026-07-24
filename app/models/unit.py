from sqlalchemy import Column, String, Integer, Float, Boolean, BigInteger, ForeignKey
from app.models.base import BaseModel

class Unit(BaseModel):
    __tablename__ = "units"

    unit_code = Column(String(20), nullable=False, unique=True, index=True)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    building = Column(String(10), nullable=True)
    floor = Column(Integer, nullable=True)
    unit_number = Column(String(10), nullable=False)
    area = Column(Float, nullable=True)
    price = Column(BigInteger, nullable=True)
    status = Column(String(20), default="AVAILABLE")
    is_active = Column(Boolean, default=True)