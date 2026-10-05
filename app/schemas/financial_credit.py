from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.jalali import JalaliDateInput
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
    contract_id: int | None = None
    credit_type: CreditType
    amount: int = Field(..., gt=0, description="مبلغ اعتبار")
    status: CreditStatus | None = CreditStatus.PENDING
    credit_date: JalaliDateInput
    description: str | None = None
    reference_id: str | None = None
    bank_account_id: int | None = None
    cheque_no: str | None = Field(None, max_length=50)

class FinancialCreditCreate(FinancialCreditBase):
    pass

class FinancialCreditUpdate(BaseModel):
    amount: int | None = Field(None, gt=0, description="مبلغ اعتبار")
    status: CreditStatus | None = None
    description: str | None = None
    bank_account_id: int | None = None
    cheque_no: str | None = Field(None, max_length=50)

class FinancialCreditResponse(FinancialCreditBase):
    id: int
    credit_no: str
    receipt_id: int | None = None
    journal_entry_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
