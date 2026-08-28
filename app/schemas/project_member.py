from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.schemas.jalali import JalaliDateInput, OptionalJalaliDateInput

class ProjectMemberBase(BaseModel):
    customer_id: int = Field(..., description="شناسه مشتری")
    project_id: int = Field(..., description="شناسه پروژه")
    join_date: JalaliDateInput = Field(..., description="تاریخ عضویت")
    status: Optional[str] = "ACTIVE"
    notes: Optional[str] = Field(None, max_length=500)

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMemberUpdate(BaseModel):
    join_date: OptionalJalaliDateInput = None
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class ProjectMemberResponse(ProjectMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True