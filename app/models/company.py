from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class Company(BaseModel):
    __tablename__ = "companies"

    name = Column(String(200), nullable=False)
    registration_no = Column(String(50), nullable=True)
    tax_id = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)