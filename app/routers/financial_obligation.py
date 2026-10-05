from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.financial_obligation import FinancialObligationCreate, FinancialObligationUpdate, FinancialObligationResponse
from app.services.financial_obligation_service import FinancialObligationService
from app.services.customer_service import CustomerService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/v1/financial-obligations", tags=["Financial Obligations"])

@router.post("/", response_model=FinancialObligationResponse, status_code=status.HTTP_201_CREATED)
def create_obligation(
    data: FinancialObligationCreate,
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
        return FinancialObligationService.create(
            db,
            data,
            posted_by=current_user.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/", response_model=List[FinancialObligationResponse])
def get_obligations(
    customer_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return FinancialObligationService.get_all(db, customer_id, project_id, skip, limit)

@router.get("/{obligation_id}", response_model=FinancialObligationResponse)
def get_obligation(obligation_id: int, db: Session = Depends(get_db)):
    obligation = FinancialObligationService.get_by_id(db, obligation_id)
    if not obligation:
        raise HTTPException(status_code=404, detail="بدهی پیدا نشد")
    return obligation

@router.put("/{obligation_id}", response_model=FinancialObligationResponse)
def update_obligation(obligation_id: int, data: FinancialObligationUpdate, db: Session = Depends(get_db)):
    obligation = FinancialObligationService.update(db, obligation_id, data)
    if not obligation:
        raise HTTPException(status_code=404, detail="بدهی پیدا نشد")
    return obligation

@router.delete("/{obligation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_obligation(obligation_id: int, db: Session = Depends(get_db)):
    try:
        if not FinancialObligationService.delete(db, obligation_id):
            raise HTTPException(status_code=404, detail="بدهی پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
