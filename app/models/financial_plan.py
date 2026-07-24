from sqlalchemy import Column, Integer, BigInteger, String, Date, Boolean, Text, Float, Numeric, Enum, ForeignKey, JSON
from app.models.base import BaseModel

class FinancialPlan(BaseModel):
    __tablename__ = "financial_plans"

    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    plan_name = Column(String(200), nullable=False)
    version = Column(Integer, default=1)
    total_amount = Column(BigInteger, nullable=False)
    installment_count = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    approved_by = Column(String(50), nullable=True)
    approved_at = Column(Date, nullable=True)