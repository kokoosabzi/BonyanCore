from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.receipt import (
    ReceiptConfirmRequest,
    ReceiptCreate,
    ReceiptResponse,
    ReceiptUpdate,
)
from app.services.receipt_service import ReceiptService


router = APIRouter(prefix="/api/v1/receipts", tags=["Receipts"])


@router.post(
    "/",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_receipt(
    data: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ReceiptService.create(
            db,
            data,
            operator_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/", response_model=list[ReceiptResponse])
def get_receipts(
    customer_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return ReceiptService.get_all(
        db,
        customer_id=customer_id,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = ReceiptService.get_by_id(db, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="فیش پیدا نشد")
    return receipt


@router.put("/{receipt_id}", response_model=ReceiptResponse)
def update_receipt(
    receipt_id: int,
    data: ReceiptUpdate,
    db: Session = Depends(get_db),
):
    try:
        receipt = ReceiptService.update(db, receipt_id, data)
        if not receipt:
            raise HTTPException(status_code=404, detail="فیش پیدا نشد")
        return receipt
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{receipt_id}/confirm", response_model=ReceiptResponse)
def confirm_receipt(
    receipt_id: int,
    data: ReceiptConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        receipt = ReceiptService.confirm(
            db,
            receipt_id,
            confirmed_by=current_user.id,
            username=current_user.username,
            allocations=data.allocations,
        )
        if not receipt:
            raise HTTPException(status_code=404, detail="فیش پیدا نشد")
        return receipt
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    try:
        if not ReceiptService.delete(db, receipt_id):
            raise HTTPException(status_code=404, detail="فیش پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
