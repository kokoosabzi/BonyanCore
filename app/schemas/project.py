from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from app.schemas.jalali import JalaliDateInput, OptionalJalaliDateInput

class ProjectBase(BaseModel):
    project_code: str = Field(..., min_length=2, max_length=2, description="کد پروژه ۲ رقمی")
    name: str = Field(..., max_length=200)
    start_date: JalaliDateInput
    status: Optional[str] = "ACTIVE"
    total_units: Optional[int] = 0
    description: Optional[str] = None

    @field_validator('project_code')
    @classmethod
    def validate_project_code(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('کد پروژه باید فقط شامل اعداد باشد')
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    start_date: OptionalJalaliDateInput = None
    status: Optional[str] = None
    total_units: Optional[int] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True