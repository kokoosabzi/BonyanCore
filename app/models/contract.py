from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class ContractType(str, enum.Enum):
    MEMBERSHIP = "MEMBERSHIP"
    FINAL_UNIT = "FINAL_UNIT"

class ContractStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Contract(BaseModel):
    __tablename__ = "contracts"

    contract_no = Column(String(50), nullable=False, unique=True, index=True)
    project_member_id = Column(BigInteger, ForeignKey("project_members.id"), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    unit_id = Column(BigInteger, ForeignKey("units.id"), nullable=True)
    final_price = Column(BigInteger, nullable=True)
    description = Column(Text, nullable=True)
    signed_by = Column(String(200), nullable=True)
    signed_date = Column(Date, nullable=True)

    project_member = relationship("ProjectMember", back_populates="contracts")
    unit = relationship("Unit")