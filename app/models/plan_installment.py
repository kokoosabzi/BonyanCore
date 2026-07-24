from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Date, Boolean
from app.models.base import BaseModel

class PlanInstallment(BaseModel):
    __tablename__ = "plan_installments"

    financial_plan_id = Column(BigInteger, ForeignKey("financial_plans.id"), nullable=False)
    installment_no = Column(Integer, nullable=False)
    amount = Column(BigInteger, nullable=False)
    due_date = Column(Date, nullable=False)
    is_paid = Column(Boolean, default=False)