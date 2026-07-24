from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from app.services.project_member_service import ProjectMemberService
from app.services.customer_service import CustomerService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/v1/project-members", tags=["Project Members"])

@router.post("/", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def create_project_member(data: ProjectMemberCreate, db: Session = Depends(get_db)):
    customer = CustomerService.get_by_id(db, data.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="مشتری پیدا نشد")
    project = ProjectService.get_by_id(db, data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="پروژه پیدا نشد")
    try:
        return ProjectMemberService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ProjectMemberResponse])
def get_project_members(
    project_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    if project_id:
        return ProjectMemberService.get_by_project(db, project_id, skip, limit)
    elif customer_id:
        return ProjectMemberService.get_by_customer(db, customer_id)
    else:
        return db.query(ProjectMember).filter(ProjectMember.is_deleted == False).offset(skip).limit(limit).all()

@router.get("/{member_id}", response_model=ProjectMemberResponse)
def get_project_member(member_id: int, db: Session = Depends(get_db)):
    member = ProjectMemberService.get_by_id(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="عضویت پیدا نشد")
    return member

@router.put("/{member_id}", response_model=ProjectMemberResponse)
def update_project_member(member_id: int, data: ProjectMemberUpdate, db: Session = Depends(get_db)):
    member = ProjectMemberService.update(db, member_id, data)
    if not member:
        raise HTTPException(status_code=404, detail="عضویت پیدا نشد")
    return member

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_member(member_id: int, db: Session = Depends(get_db)):
    if not ProjectMemberService.delete(db, member_id):
        raise HTTPException(status_code=404, detail="عضویت پیدا نشد")