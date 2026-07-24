from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class BulkImportType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    MEMBER = "MEMBER"
    BANK_STATEMENT = "BANK_STATEMENT"

class DebitType(str, Enum):
    PROJECT_PLAN = "PROJECT_PLAN"
    UNIT_DIFFERENCE = "UNIT_DIFFERENCE"
    PENALTY = "PENALTY"
    SERVICE_FEE = "SERVICE_FEE"
    OTHER = "OTHER"

class CreditType(str, Enum):
    LOAN = "LOAN"
    SUBSIDY = "SUBSIDY"
    DISCOUNT = "DISCOUNT"
    CHEQUE = "CHEQUE"
    OTHER = "OTHER"

class BulkImportRow(BaseModel):
    member_no: str
    full_name: Optional[str] = None
    amount: Optional[int] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    account_no: Optional[str] = None
    transaction_type: Optional[str] = None

class BulkImportCreate(BaseModel):
    import_type: BulkImportType
    project_id: int
    document_date: date
    document_description: str
    debit_type: Optional[DebitType] = None
    credit_type: Optional[CreditType] = None
    rows: List[BulkImportRow] = []

class BulkImportResponse(BaseModel):
    success: bool
    message: str
    journal_no: Optional[str] = None
    total_rows: int = 0
    total_amount: int = 0
    errors: Optional[List[str]] = None