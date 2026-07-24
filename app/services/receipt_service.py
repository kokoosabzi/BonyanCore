from sqlalchemy.orm import Session
from app.models.receipt import Receipt, PaymentMethod, ReceiptStatus
from app.schemas.receipt import ReceiptCreate, ReceiptUpdate
from app.services.document_sequence_service import DocumentSequenceService

class ReceiptService:
    @staticmethod
    def create(db: Session, data: ReceiptCreate) -> Receipt:
        receipt_no = DocumentSequenceService.get_next_receipt_number(db)
        receipt = Receipt(receipt_no=receipt_no, **data.model_dump())
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def get_by_id(db: Session, receipt_id: int) -> Receipt | None:
        return db.query(Receipt).filter(
            Receipt.id == receipt_id,
            Receipt.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(Receipt).filter(Receipt.is_deleted == False)
        if customer_id:
            query = query.filter(Receipt.customer_id == customer_id)
        if project_id:
            query = query.filter(Receipt.project_id == project_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, receipt_id: int, data: ReceiptUpdate) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(receipt, key, value)
        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def delete(db: Session, receipt_id: int) -> bool:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return False
        receipt.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def confirm(db: Session, receipt_id: int) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return None
        receipt.status = ReceiptStatus.CONFIRMED
        db.commit()
        db.refresh(receipt)
        return receipt