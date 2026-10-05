from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.transfer import Transfer
from app.services.bank_account_service import BankAccountService
from app.services.document_sequence_service import DocumentSequenceService
from app.utils.jalali import parse_jalali_date


router = APIRouter(prefix="/api/v1/transfers", tags=["Transfers"])


@router.post("/")
async def create_transfer(
    from_account_id: int = Form(...),
    to_account_id: int = Form(...),
    amount: int = Form(..., gt=0),
    transfer_date: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=400,
            detail="حساب مبدأ و مقصد باید متفاوت باشند",
        )
    if not BankAccountService.get_by_id(db, from_account_id):
        raise HTTPException(status_code=404, detail="حساب مبدأ پیدا نشد")
    if not BankAccountService.get_by_id(db, to_account_id):
        raise HTTPException(status_code=404, detail="حساب مقصد پیدا نشد")

    try:
        parsed_date = parse_jalali_date(transfer_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    transfer = Transfer(
        transfer_no=DocumentSequenceService.get_next_transfer_number(db),
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        amount=amount,
        transfer_date=parsed_date,
        description=description if description else None,
    )
    db.add(transfer)
    db.commit()
    return RedirectResponse("/pages/transfers?created=1", status_code=303)
