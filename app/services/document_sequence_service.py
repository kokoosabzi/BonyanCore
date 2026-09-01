from sqlalchemy.orm import Session
from app.models.document_sequence import DocumentSequence
import jdatetime

class DocumentSequenceService:
    @staticmethod
    def get_next_number(db: Session, prefix: str) -> str:
        now = jdatetime.datetime.now()
        year = str(now.year % 100).zfill(2)
        sequence = db.query(DocumentSequence).filter(
            DocumentSequence.prefix == prefix,
            DocumentSequence.year == year
        ).first()
        if not sequence:
            sequence = DocumentSequence(prefix=prefix, year=year, current_number=0)
            db.add(sequence)
            db.flush()
        sequence.current_number += 1
        db.flush()
        return f"{prefix}-{year}-{sequence.current_number:06d}"

    @staticmethod
    def get_next_contract_number(db: Session) -> str:
        return DocumentSequenceService.get_next_number(db, "CTR")

    @staticmethod
    def get_next_obligation_number(db: Session) -> str:
        return DocumentSequenceService.get_next_number(db, "OBL")

    @staticmethod
    def get_next_credit_number(db: Session) -> str:
        return DocumentSequenceService.get_next_number(db, "CRD")

    @staticmethod
    def get_next_receipt_number(db: Session) -> str:
        return DocumentSequenceService.get_next_number(db, "RCV")

    @staticmethod
    def get_next_payment_number(db: Session) -> str:
        return DocumentSequenceService.get_next_number(db, "PAY")

    @staticmethod
    def get_next_journal_number(db: Session) -> str:
        return DocumentSequenceService.get_next_number(db, "JV")