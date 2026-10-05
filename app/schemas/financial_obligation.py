from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.schemas.jalali import JalaliDateInput, OptionalJalaliDateInput
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
    project_member_id: Optional[int] = None
    contract_id: Optional[int] = None
    obligation_type: ObligationType
    amount: int = Field(..., gt=0, description="مبلغ بدهی")
    due_date: OptionalJalaliDateInput = None
    description: Optional[str] = None
    reference_id: Optional[str] = None

class FinancialObligationCreate(FinancialObligationBase):
    pass

class FinancialObligationUpdate(BaseModel):
    due_date: OptionalJalaliDateInput = None
    description: Optional[str] = None

class FinancialObligationResponse(FinancialObligationBase):
    id: int
    obligation_no: str
    paid_amount: int
    status: ObligationStatus
    journal_entry_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
