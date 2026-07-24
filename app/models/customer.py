from sqlalchemy import Column, String, Date, Boolean, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"

    customer_no = Column(String(6), nullable=False, unique=True, index=True)
    full_name = Column(String(200), nullable=False)
    national_code = Column(String(10), unique=True, nullable=True)
    birth_date = Column(Date, nullable=True)
    mobile = Column(String(11), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    job = Column(String(100), nullable=True)
    status = Column(String(20), default="ACTIVE")
    dynamic_data = Column(Text, nullable=True)

    project_members = relationship("ProjectMember", back_populates="customer")