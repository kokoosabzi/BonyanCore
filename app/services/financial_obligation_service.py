from sqlalchemy.orm import Session
from app.models.financial_obligation import FinancialObligation, ObligationType, ObligationStatus
from app.schemas.financial_obligation import FinancialObligationCreate, FinancialObligationUpdate
from app.services.document_sequence_service import DocumentSequenceService

class FinancialObligationService:
    @staticmethod
    def create(db: Session, data: FinancialObligationCreate) -> FinancialObligation:
        obligation_no = DocumentSequenceService.get_next_obligation_number(db)
        obligation = FinancialObligation(obligation_no=obligation_no, **data.model_dump())
        db.add(obligation)
        db.commit()
        db.refresh(obligation)
        return obligation

    @staticmethod
    def get_by_id(db: Session, obligation_id: int) -> FinancialObligation | None:
        return db.query(FinancialObligation).filter(
            FinancialObligation.id == obligation_id,
            FinancialObligation.is_deleted == False
        ).first()

    @staticmethod
    def get_by_customer(db: Session, customer_id: int):
        return db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == customer_id,
            FinancialObligation.is_deleted == False
        ).all()

    @staticmethod
    def get_by_project(db: Session, project_id: int):
        return db.query(FinancialObligation).filter(
            FinancialObligation.project_id == project_id,
            FinancialObligation.is_deleted == False
        ).all()

    @staticmethod
    def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(FinancialObligation).filter(FinancialObligation.is_deleted == False)
        if customer_id:
            query = query.filter(FinancialObligation.customer_id == customer_id)
        if project_id:
            query = query.filter(FinancialObligation.project_id == project_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, obligation_id: int, data: FinancialObligationUpdate) -> FinancialObligation | None:
        obligation = FinancialObligationService.get_by_id(db, obligation_id)
        if not obligation:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obligation, key, value)
        db.commit()
        db.refresh(obligation)
        return obligation

    @staticmethod
    def delete(db: Session, obligation_id: int) -> bool:
        obligation = FinancialObligationService.get_by_id(db, obligation_id)
        if not obligation:
            return False
        obligation.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def get_total_obligations(db: Session, customer_id: int) -> int:
        total = db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == customer_id,
            FinancialObligation.is_deleted == False,
            FinancialObligation.status != ObligationStatus.CANCELLED
        ).with_entities(FinancialObligation.amount).all()
        return sum([t[0] for t in total]) if total else 0