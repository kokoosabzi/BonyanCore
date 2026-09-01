from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService
router=APIRouter(prefix="/api/v1/payments", tags=["Payments"])
@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create(data: PaymentCreate, db: Session=Depends(get_db)): return PaymentService.create(db,data)
@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm(payment_id:int, db:Session=Depends(get_db)):
    try: payment=PaymentService.confirm(db,payment_id)
    except ValueError as exc: raise HTTPException(400, str(exc))
    if not payment: raise HTTPException(404,"پرداخت پیدا نشد")
    return payment
@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
def cancel(payment_id:int, db:Session=Depends(get_db)):
    try: payment=PaymentService.cancel(db,payment_id)
    except ValueError as exc: raise HTTPException(400,str(exc))
    if not payment: raise HTTPException(404,"پرداخت پیدا نشد")
    return payment
