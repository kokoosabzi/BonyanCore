from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class ProjectMemberBase(BaseModel):
    customer_id: int = Field(..., description="شناسه مشتری")
    project_id: int = Field(..., description="شناسه پروژه")
    join_date: date = Field(..., description="تاریخ عضویت")
    status: Optional[str] = "ACTIVE"
    notes: Optional[str] = Field(None, max_length=500)

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMemberUpdate(BaseModel):
    join_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class ProjectMemberResponse(ProjectMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True