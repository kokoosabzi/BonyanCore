from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.jalali import JalaliDateInput, OptionalJalaliDateInput


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    DEPOSIT_SLIP = "DEPOSIT_SLIP"
    TRANSFER = "TRANSFER"
    POS = "POS"
    OTHER = "OTHER"


class ReceiptStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class ReceiptBase(BaseModel):
    customer_id: int
    project_id: int
    project_member_id: Optional[int] = None
    contract_id: Optional[int] = None
    amount: int = Field(..., gt=0)
    receipt_date: JalaliDateInput
    payment_method: PaymentMethod
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = None
    cheque_due_date: OptionalJalaliDateInput = None
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=150)
    drawer_name: Optional[str] = Field(None, max_length=200)
    payee_name: Optional[str] = Field(None, max_length=200)
    deposit_document_type: Optional[str] = Field(None, max_length=100)
    depositor_name: Optional[str] = Field(None, max_length=200)
    reference_no: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[ReceiptStatus] = ReceiptStatus.DRAFT

    @model_validator(mode="after")
    def validate_payment_details(self):
        if self.payment_method == PaymentMethod.CHEQUE:
            if not self.cheque_no or not self.cheque_due_date:
                raise ValueError("شماره و تاریخ سررسید چک الزامی است")
        if self.payment_method in {
            PaymentMethod.DEPOSIT_SLIP,
            PaymentMethod.TRANSFER,
            PaymentMethod.POS,
        } and not self.bank_account_id:
            raise ValueError("انتخاب حساب بانکی برای این روش پرداخت الزامی است")
        return self


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    amount: Optional[int] = Field(None, gt=0)
    receipt_date: OptionalJalaliDateInput = None
    payment_method: Optional[PaymentMethod] = None
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = None
    cheque_due_date: OptionalJalaliDateInput = None
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=150)
    drawer_name: Optional[str] = Field(None, max_length=200)
    payee_name: Optional[str] = Field(None, max_length=200)
    deposit_document_type: Optional[str] = Field(None, max_length=100)
    depositor_name: Optional[str] = Field(None, max_length=200)
    reference_no: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class ReceiptAllocationInput(BaseModel):
    obligation_id: int
    amount: int = Field(..., gt=0)


class ReceiptConfirmRequest(BaseModel):
    allocations: list[ReceiptAllocationInput] = Field(default_factory=list)


class ReceiptResponse(ReceiptBase):
    id: int
    receipt_no: str
    amount_in_words: str
    operator_id: Optional[int] = None
    confirmed_by: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    journal_entry_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
