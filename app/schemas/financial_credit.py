from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum

class CreditType(str, Enum):
    PAYMENT = "PAYMENT"
    LOAN = "LOAN"
    SUBSIDY = "SUBSIDY"
    DISCOUNT = "DISCOUNT"
    DECREASE_ADJUSTMENT = "DECREASE_ADJUSTMENT"
    OTHER = "OTHER"

class CreditStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REVERSED = "REVERSED"

class FinancialCreditBase(BaseModel):
    customer_id: int
    project_id: int
    contract_id: Optional[int] = None
    credit_type: CreditType
    amount: int = Field(..., gt=0, description="مبلغ اعتبار")
    status: Optional[CreditStatus] = CreditStatus.PENDING
    credit_date: date
    description: Optional[str] = None
    reference_id: Optional[str] = None
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = Field(None, max_length=50)

class FinancialCreditCreate(FinancialCreditBase):
    pass

class FinancialCreditUpdate(BaseModel):
    amount: Optional[int] = None
    status: Optional[CreditStatus] = None
    description: Optional[str] = None
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = Field(None, max_length=50)

class FinancialCreditResponse(FinancialCreditBase):
    id: int
    credit_no: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True