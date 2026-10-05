from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1/bank-statements", tags=["Bank Statements"])

class BankStatementReconcileRequest(BaseModel):
    receipt_id: Optional[int] = None
    payment_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_target(self):
        if (self.receipt_id is None) == (self.payment_id is None):
            raise ValueError("دقیقاً یکی از receipt_id یا payment_id باید مشخص شود")
        return self

@router.post("/{statement_id}/reconcile")
def reconcile_bank_statement(statement_id: int, data: BankStatementReconcileRequest,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    try:
        statement = ReportService.reconcile_bank_statement(
            db, statement_id, receipt_id=data.receipt_id, payment_id=data.payment_id
        )
        return {
            "message": "تطبیق بانکی با موفقیت ثبت شد",
            "statement_id": statement.id,
            "receipt_id": statement.receipt_id,
            "payment_id": statement.payment_id,
            "is_reconciled": statement.is_reconciled,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.delete("/{statement_id}/reconcile")
def unreconcile_bank_statement(statement_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    try:
        statement = ReportService.unreconcile_bank_statement(db, statement_id)
        return {"message": "تطبیق بانکی حذف شد", "statement_id": statement.id,
                "is_reconciled": statement.is_reconciled}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
