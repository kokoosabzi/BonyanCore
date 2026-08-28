from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum
from app.utils.jalali import normalize_date_text, parse_jalali_date, to_jalali

class JournalStatus(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"

class JournalLineBase(BaseModel):
    account_id: int
    debit: Optional[int] = Field(None, ge=0)
    credit: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    analytic_account_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_single_sided_amount(self):
        debit = self.debit or 0
        credit = self.credit or 0
        if debit <= 0 and credit <= 0:
            raise ValueError('هر ردیف سند باید مبلغ بدهکار یا بستانکار داشته باشد')
        if debit > 0 and credit > 0:
            raise ValueError('هر ردیف فقط می‌تواند بدهکار یا بستانکار باشد')
        return self

class JournalLineCreate(JournalLineBase):
    pass

class JournalLineResponse(JournalLineBase):
    id: int
    journal_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JournalEntryBase(BaseModel):
    journal_date: str = Field(..., description="تاریخ سند به شمسی (مثال: 1404/05/03)")
    status: Optional[JournalStatus] = JournalStatus.DRAFT
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None

    @field_validator('journal_date', mode="before")
    @classmethod
    def validate_jalali_date(cls, v: str | date) -> str:
        """Validate and normalize Jalali date text before service conversion."""
        if isinstance(v, date):
            return to_jalali(v)
        parse_jalali_date(v)
        normalized = normalize_date_text(v)
        year, month, day = normalized.split('-')
        return f"{int(year):04d}/{int(month):02d}/{int(day):02d}"

class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalLineCreate] = Field(default_factory=list, min_length=2)

    @model_validator(mode="after")
    def validate_balanced_lines(self):
        total_debit = sum(line.debit or 0 for line in self.lines)
        total_credit = sum(line.credit or 0 for line in self.lines)
        if total_debit != total_credit:
            raise ValueError('جمع بدهکار و بستانکار باید برابر باشد')
        return self

class JournalEntryUpdate(BaseModel):
    journal_date: Optional[str] = None
    status: Optional[JournalStatus] = None
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    lines: Optional[List[JournalLineCreate]] = None

    @field_validator('journal_date', mode="before")
    @classmethod
    def validate_optional_jalali_date(cls, v: Optional[str | date]) -> Optional[str]:
        if not v:
            return v
        if isinstance(v, date):
            return to_jalali(v)
        parse_jalali_date(v)
        normalized = normalize_date_text(v)
        year, month, day = normalized.split('-')
        return f"{int(year):04d}/{int(month):02d}/{int(day):02d}"

    @model_validator(mode="after")
    def validate_balanced_lines_when_provided(self):
        if self.lines is None:
            return self
        if len(self.lines) < 2:
            raise ValueError('حداقل دو ردیف معتبر برای سند حسابداری لازم است')
        total_debit = sum(line.debit or 0 for line in self.lines)
        total_credit = sum(line.credit or 0 for line in self.lines)
        if total_debit != total_credit:
            raise ValueError('جمع بدهکار و بستانکار باید برابر باشد')
        return self

class JournalEntryResponse(JournalEntryBase):
    id: int
    journal_no: str
    created_at: datetime
    updated_at: datetime
    lines: List[JournalLineResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True