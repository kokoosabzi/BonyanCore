from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.bank_reconciliation_service import BankReconciliationService
router=APIRouter(prefix="/api/v1/bank-reconciliation", tags=["Bank Reconciliation"])
class MatchRequest(BaseModel): source_type:str; source_id:int; confirmed:bool=False
@router.put("/{statement_id}/match")
def save_match(statement_id:int, data:MatchRequest, db:Session=Depends(get_db)):
    result=BankReconciliationService.save_match(db,statement_id,data.source_type,data.source_id,data.confirmed)
    if not result: raise HTTPException(404,"ردیف صورت‌حساب پیدا نشد")
    return result
@router.post("/{statement_id}/confirm")
def confirm(statement_id:int, db:Session=Depends(get_db)):
    result=BankReconciliationService.confirm(db,statement_id)
    if not result: raise HTTPException(404,"تطبیق ثبت نشده است")
    return result
