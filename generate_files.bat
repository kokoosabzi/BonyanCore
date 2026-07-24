@echo off
echo Generating Bonyan Core files...

REM ============================================
REM Financial Credit
REM ============================================
echo Creating app/schemas/financial_credit.py ...
(
echo from pydantic import BaseModel, Field
echo from typing import Optional
echo from datetime import date, datetime
echo from enum import Enum
echo.
echo class CreditType(str, Enum^):
echo     PAYMENT = "PAYMENT"
echo     LOAN = "LOAN"
echo     SUBSIDY = "SUBSIDY"
echo     DISCOUNT = "DISCOUNT"
echo     DECREASE_ADJUSTMENT = "DECREASE_ADJUSTMENT"
echo     OTHER = "OTHER"
echo.
echo class CreditStatus(str, Enum^):
echo     PENDING = "PENDING"
echo     APPROVED = "APPROVED"
echo     REVERSED = "REVERSED"
echo.
echo class FinancialCreditBase(BaseModel^):
echo     customer_id: int
echo     project_id: int
echo     contract_id: Optional[int] = None
echo     credit_type: CreditType
echo     amount: int = Field(...^, gt=0^, description="مبلغ اعتبار"^)
echo     status: Optional[CreditStatus] = CreditStatus.PENDING
echo     credit_date: date
echo     description: Optional[str] = None
echo     reference_id: Optional[str] = None
echo     bank_account_id: Optional[int] = None
echo     cheque_no: Optional[str] = Field(None^, max_length=50^)
echo.
echo class FinancialCreditCreate(FinancialCreditBase^):
echo     pass
echo.
echo class FinancialCreditUpdate(BaseModel^):
echo     amount: Optional[int] = None
echo     status: Optional[CreditStatus] = None
echo     description: Optional[str] = None
echo     bank_account_id: Optional[int] = None
echo     cheque_no: Optional[str] = Field(None^, max_length=50^)
echo.
echo class FinancialCreditResponse(FinancialCreditBase^):
echo     id: int
echo     credit_no: str
echo     created_at: datetime
echo     updated_at: datetime
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\financial_credit.py

echo Creating app/services/financial_credit_service.py ...
(
echo from sqlalchemy.orm import Session
echo from app.models.financial_credit import FinancialCredit, CreditType, CreditStatus
echo from app.schemas.financial_credit import FinancialCreditCreate, FinancialCreditUpdate
echo from app.services.document_sequence_service import DocumentSequenceService
echo.
echo class FinancialCreditService:
echo     @staticmethod
echo     def create(db: Session, data: FinancialCreditCreate^) -> FinancialCredit:
echo         credit_no = DocumentSequenceService.get_next_credit_number(db^)
echo         credit = FinancialCredit(credit_no=credit_no, **data.model_dump(^)^)
echo         db.add(credit^)
echo         db.commit(^)
echo         db.refresh(credit^)
echo         return credit
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, credit_id: int^) -> FinancialCredit ^| None:
echo         return db.query(FinancialCredit^).filter(FinancialCredit.id == credit_id, FinancialCredit.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_customer(db: Session, customer_id: int^):
echo         return db.query(FinancialCredit^).filter(FinancialCredit.customer_id == customer_id, FinancialCredit.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def get_by_project(db: Session, project_id: int^):
echo         return db.query(FinancialCredit^).filter(FinancialCredit.project_id == project_id, FinancialCredit.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100^):
echo         query = db.query(FinancialCredit^).filter(FinancialCredit.is_deleted == False^)
echo         if customer_id:
echo             query = query.filter(FinancialCredit.customer_id == customer_id^)
echo         if project_id:
echo             query = query.filter(FinancialCredit.project_id == project_id^)
echo         return query.offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, credit_id: int, data: FinancialCreditUpdate^) -> FinancialCredit ^| None:
echo         credit = FinancialCreditService.get_by_id(db, credit_id^)
echo         if not credit:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(credit, key, value^)
echo         db.commit(^)
echo         db.refresh(credit^)
echo         return credit
echo.
echo     @staticmethod
echo     def delete(db: Session, credit_id: int^) -> bool:
echo         credit = FinancialCreditService.get_by_id(db, credit_id^)
echo         if not credit:
echo             return False
echo         credit.is_deleted = True
echo         db.commit(^)
echo         return True
echo.
echo     @staticmethod
echo     def get_total_credits(db: Session, customer_id: int^) -> int:
echo         total = db.query(FinancialCredit^).filter(FinancialCredit.customer_id == customer_id, FinancialCredit.is_deleted == False, FinancialCredit.status != CreditStatus.REVERSED^).with_entities(FinancialCredit.amount^).all(^)
echo         return sum([t[0] for t in total]^) if total else 0
echo.
echo     @staticmethod
echo     def get_net_balance(db: Session, customer_id: int^) -> int:
echo         from app.services.financial_obligation_service import FinancialObligationService
echo         total_obligations = FinancialObligationService.get_total_obligations(db, customer_id^)
echo         total_credits = FinancialCreditService.get_total_credits(db, customer_id^)
echo         return total_obligations - total_credits
) > app\services\financial_credit_service.py

echo Creating app/routers/financial_credit.py ...
(
echo from fastapi import APIRouter, Depends, HTTPException, Query, status
echo from sqlalchemy.orm import Session
echo from typing import Optional, List
echo from app.core.database import get_db
echo from app.schemas.financial_credit import FinancialCreditCreate, FinancialCreditUpdate, FinancialCreditResponse
echo from app.services.financial_credit_service import FinancialCreditService
echo from app.services.customer_service import CustomerService
echo from app.services.project_service import ProjectService
echo.
echo router = APIRouter(prefix="/api/v1/financial-credits", tags=["Financial Credits"]^)
echo.
echo @router.post("/", response_model=FinancialCreditResponse, status_code=status.HTTP_201_CREATED^)
echo def create_credit(data: FinancialCreditCreate, db: Session = Depends(get_db^)^):
echo     customer = CustomerService.get_by_id(db, data.customer_id^)
echo     if not customer:
echo         raise HTTPException(status_code=404, detail="مشتری پیدا نشد"^)
echo     project = ProjectService.get_by_id(db, data.project_id^)
echo     if not project:
echo         raise HTTPException(status_code=404, detail="پروژه پیدا نشد"^)
echo     return FinancialCreditService.create(db, data^)
echo.
echo @router.get("/", response_model=List[FinancialCreditResponse]^)
echo def get_credits(customer_id: Optional[int] = Query(None^), project_id: Optional[int] = Query(None^), skip: int = Query(0, ge=0^), limit: int = Query(100, ge=1, le=1000^), db: Session = Depends(get_db^)^):
echo     return FinancialCreditService.get_all(db, customer_id, project_id, skip, limit^)
echo.
echo @router.get("/{credit_id}", response_model=FinancialCreditResponse^)
echo def get_credit(credit_id: int, db: Session = Depends(get_db^)^):
echo     credit = FinancialCreditService.get_by_id(db, credit_id^)
echo     if not credit:
echo         raise HTTPException(status_code=404, detail="اعتبار پیدا نشد"^)
echo     return credit
echo.
echo @router.put("/{credit_id}", response_model=FinancialCreditResponse^)
echo def update_credit(credit_id: int, data: FinancialCreditUpdate, db: Session = Depends(get_db^)^):
echo     credit = FinancialCreditService.update(db, credit_id, data^)
echo     if not credit:
echo         raise HTTPException(status_code=404, detail="اعتبار پیدا نشد"^)
echo     return credit
echo.
echo @router.delete("/{credit_id}", status_code=status.HTTP_204_NO_CONTENT^)
echo def delete_credit(credit_id: int, db: Session = Depends(get_db^)^):
echo     if not FinancialCreditService.delete(db, credit_id^):
echo         raise HTTPException(status_code=404, detail="اعتبار پیدا نشد"^)
) > app\routers\financial_credit.py

echo.
echo All files generated successfully!
pause