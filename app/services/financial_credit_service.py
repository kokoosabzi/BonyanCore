from sqlalchemy.orm import Session
from app.models.financial_credit import FinancialCredit, CreditType, CreditStatus
from app.schemas.financial_credit import FinancialCreditCreate, FinancialCreditUpdate
from app.services.document_sequence_service import DocumentSequenceService

class FinancialCreditService:
    @staticmethod
    def create(db: Session, data: FinancialCreditCreate) -> FinancialCredit:
        credit_no = DocumentSequenceService.get_next_credit_number(db)
        credit = FinancialCredit(credit_no=credit_no, **data.model_dump())
        db.add(credit)
        db.commit()
        db.refresh(credit)
        return credit

    @staticmethod
    def get_by_id(db: Session, credit_id: int) -> FinancialCredit | None:
        return db.query(FinancialCredit).filter(
            FinancialCredit.id == credit_id,
            FinancialCredit.is_deleted == False
        ).first()

    @staticmethod
    def get_by_customer(db: Session, customer_id: int):
        return db.query(FinancialCredit).filter(
            FinancialCredit.customer_id == customer_id,
            FinancialCredit.is_deleted == False
        ).all()

    @staticmethod
    def get_by_project(db: Session, project_id: int):
        return db.query(FinancialCredit).filter(
            FinancialCredit.project_id == project_id,
            FinancialCredit.is_deleted == False
        ).all()

    @staticmethod
    def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(FinancialCredit).filter(FinancialCredit.is_deleted == False)
        if customer_id:
            query = query.filter(FinancialCredit.customer_id == customer_id)
        if project_id:
            query = query.filter(FinancialCredit.project_id == project_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, credit_id: int, data: FinancialCreditUpdate) -> FinancialCredit | None:
        credit = FinancialCreditService.get_by_id(db, credit_id)
        if not credit:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(credit, key, value)
        db.commit()
        db.refresh(credit)
        return credit

    @staticmethod
    def delete(db: Session, credit_id: int) -> bool:
        credit = FinancialCreditService.get_by_id(db, credit_id)
        if not credit:
            return False
        credit.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def get_total_credits(db: Session, customer_id: int) -> int:
        total = db.query(FinancialCredit).filter(
            FinancialCredit.customer_id == customer_id,
            FinancialCredit.is_deleted == False,
            FinancialCredit.status != CreditStatus.REVERSED
        ).with_entities(FinancialCredit.amount).all()
        return sum([t[0] for t in total]) if total else 0

    @staticmethod
    def get_net_balance(db: Session, customer_id: int) -> int:
        from app.services.financial_obligation_service import FinancialObligationService
        total_obligations = FinancialObligationService.get_total_obligations(db, customer_id)
        total_credits = FinancialCreditService.get_total_credits(db, customer_id)
        return total_obligations - total_credits