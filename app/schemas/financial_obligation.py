from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum

class ObligationType(str, Enum):
    PROJECT_PLAN = "PROJECT_PLAN"
    UNIT_DIFFERENCE = "UNIT_DIFFERENCE"
    PENALTY = "PENALTY"
    INCREASE_ADJUSTMENT = "INCREASE_ADJUSTMENT"
    SERVICE_FEE = "SERVICE_FEE"
    OTHER = "OTHER"

class ObligationStatus(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class FinancialObligationBase(BaseModel):
    customer_id: int
    project_id: int
    contract_id: Optional[int] = None
    obligation_type: ObligationType
    amount: int = Field(..., gt=0, description="مبلغ بدهی")
    paid_amount: Optional[int] = 0
    status: Optional[ObligationStatus] = ObligationStatus.PENDING
    due_date: Optional[date] = None
    description: Optional[str] = None
    reference_id: Optional[str] = None

class FinancialObligationCreate(FinancialObligationBase):
    pass

class FinancialObligationUpdate(BaseModel):
    paid_amount: Optional[int] = None
    status: Optional[ObligationStatus] = None
    due_date: Optional[date] = None
    description: Optional[str] = None

class FinancialObligationResponse(FinancialObligationBase):
    id: int
    obligation_no: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True