from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.receipt import ReceiptCreate, ReceiptResponse, ReceiptUpdate
from app.services.receipt_service import ReceiptService

router = APIRouter(prefix="/api/v1/receipts", tags=["Receipts"])


@router.post("/", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt(data: ReceiptCreate, db: Session = Depends(get_db)):
    try:
        return ReceiptService.create(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/", response_model=List[ReceiptResponse])
def list_receipts(customer_id: Optional[int] = None, project_id: Optional[int] = None,
                  skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    return ReceiptService.get_all(db, customer_id, project_id, skip, limit)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = ReceiptService.get_by_id(db, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="دریافت پیدا نشد")
    return receipt


@router.put("/{receipt_id}", response_model=ReceiptResponse)
def update_receipt(receipt_id: int, data: ReceiptUpdate, db: Session = Depends(get_db)):
    try:
        receipt = ReceiptService.update(db, receipt_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not receipt:
        raise HTTPException(status_code=404, detail="دریافت پیدا نشد")
    return receipt


@router.post("/{receipt_id}/confirm", response_model=ReceiptResponse)
def confirm_receipt(receipt_id: int, db: Session = Depends(get_db)):
    try:
        receipt = ReceiptService.confirm(db, receipt_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not receipt:
        raise HTTPException(status_code=404, detail="دریافت پیدا نشد")
    return receipt


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    try:
        deleted = ReceiptService.delete(db, receipt_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not deleted:
        raise HTTPException(status_code=404, detail="دریافت پیدا نشد")

@router.post("/{receipt_id}/collect-cheque", response_model=ReceiptResponse)
def collect_cheque(receipt_id: int, db: Session = Depends(get_db)):
    try:
        receipt = ReceiptService.collect_cheque(db, receipt_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not receipt:
        raise HTTPException(status_code=404, detail="دریافت پیدا نشد")
    return receipt

@router.post("/{receipt_id}/return-cheque", response_model=ReceiptResponse)
def return_cheque(receipt_id: int, reason: str | None = None, db: Session = Depends(get_db)):
    try: receipt = ReceiptService.return_cheque(db, receipt_id, reason)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc))
    if not receipt: raise HTTPException(status_code=404, detail="دریافت پیدا نشد")
    return receipt

@router.post("/{receipt_id}/cancel", response_model=ReceiptResponse)
def cancel_receipt(receipt_id: int, db: Session = Depends(get_db)):
    try: receipt = ReceiptService.cancel(db, receipt_id)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc))
    if not receipt: raise HTTPException(status_code=404, detail="دریافت پیدا نشد")
    return receipt
