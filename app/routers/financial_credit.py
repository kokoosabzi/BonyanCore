from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.financial_credit import FinancialCreditCreate, FinancialCreditUpdate, FinancialCreditResponse
from app.services.financial_credit_service import FinancialCreditService
from app.services.customer_service import CustomerService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/v1/financial-credits", tags=["Financial Credits"])

@router.post("/", response_model=FinancialCreditResponse, status_code=status.HTTP_201_CREATED)
def create_credit(
    data: FinancialCreditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = CustomerService.get_by_id(db, data.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="مشتری پیدا نشد")
    project = ProjectService.get_by_id(db, data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="پروژه پیدا نشد")
    try:
        return FinancialCreditService.create(
            db,
            data,
            posted_by=current_user.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/", response_model=List[FinancialCreditResponse])
def get_credits(
    customer_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return FinancialCreditService.get_all(db, customer_id, project_id, skip, limit)

@router.get("/{credit_id}", response_model=FinancialCreditResponse)
def get_credit(credit_id: int, db: Session = Depends(get_db)):
    credit = FinancialCreditService.get_by_id(db, credit_id)
    if not credit:
        raise HTTPException(status_code=404, detail="اعتبار پیدا نشد")
    return credit

@router.put("/{credit_id}", response_model=FinancialCreditResponse)
def update_credit(credit_id: int, data: FinancialCreditUpdate, db: Session = Depends(get_db)):
    try:
        credit = FinancialCreditService.update(db, credit_id, data)
        if not credit:
            raise HTTPException(status_code=404, detail="اعتبار پیدا نشد")
        return credit
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.delete("/{credit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credit(credit_id: int, db: Session = Depends(get_db)):
    try:
        if not FinancialCreditService.delete(db, credit_id):
            raise HTTPException(status_code=404, detail="اعتبار پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
