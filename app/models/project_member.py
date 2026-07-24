from sqlalchemy import Column, String, Date, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class ProjectMember(BaseModel):
    __tablename__ = "project_members"

    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    join_date = Column(Date, nullable=False)
    status = Column(String(20), default="ACTIVE")
    notes = Column(String(500), nullable=True)

    customer = relationship("Customer", back_populates="project_members")
    project = relationship("Project")
    contracts = relationship("Contract", back_populates="project_member")