from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry, JournalStatus
from app.models.journal_line import DebitCredit, JournalLine
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryUpdate, JournalLineCreate
from app.services.document_sequence_service import DocumentSequenceService
from app.utils.jalali import to_gregorian


class JournalEntryService:
    @staticmethod
    def _build_line(journal_id: int, line_data: JournalLineCreate) -> JournalLine:
        debit = line_data.debit or 0
        credit = line_data.credit or 0
        if debit > 0 and credit > 0:
            raise ValueError("هر ردیف فقط می‌تواند بدهکار یا بستانکار باشد")
        if debit <= 0 and credit <= 0:
            raise ValueError("هر ردیف سند باید مبلغ بدهکار یا بستانکار داشته باشد")

        return JournalLine(
            journal_id=journal_id,
            account_id=line_data.account_id,
            debit_credit=DebitCredit.DEBIT if debit > 0 else DebitCredit.CREDIT,
            amount=debit if debit > 0 else credit,
            description=line_data.description,
            analytic_account_id=line_data.analytic_account_id,
        )

    @staticmethod
    def _validate_balanced_lines(lines: Iterable[JournalLine]) -> None:
        lines = list(lines)
        if len(lines) < 2:
            raise ValueError("حداقل دو ردیف معتبر برای سند حسابداری لازم است")

        total_debit = sum(line.amount for line in lines if line.debit_credit == DebitCredit.DEBIT)
        total_credit = sum(line.amount for line in lines if line.debit_credit == DebitCredit.CREDIT)
        if total_debit != total_credit:
            raise ValueError("جمع بدهکار و بستانکار باید برابر باشد")

    @staticmethod
    def create(db: Session, data: JournalEntryCreate) -> JournalEntry:
        journal_no = DocumentSequenceService.get_next_journal_number(db)
        journal_date = to_gregorian(data.journal_date)

        status = data.status or JournalStatus.DRAFT
        journal = JournalEntry(
            journal_no=journal_no,
            journal_date=journal_date,
            status=status,
            description=data.description,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            posted_at=datetime.utcnow() if status == JournalStatus.POSTED else None,
        )
        db.add(journal)
        db.flush()

        lines = [JournalEntryService._build_line(journal.id, line_data) for line_data in data.lines]
        JournalEntryService._validate_balanced_lines(lines)
        db.add_all(lines)

        db.commit()
        db.refresh(journal)
        return journal

    @staticmethod
    def get_by_id(db: Session, journal_id: int) -> JournalEntry | None:
        return db.query(JournalEntry).filter(
            JournalEntry.id == journal_id,
            JournalEntry.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, status: str = None):
        query = db.query(JournalEntry).filter(JournalEntry.is_deleted == False)
        if status:
            query = query.filter(JournalEntry.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, journal_id: int, data: JournalEntryUpdate) -> JournalEntry | None:
        journal = JournalEntryService.get_by_id(db, journal_id)
        if not journal:
            return None
        if journal.status == JournalStatus.POSTED:
            raise ValueError("سند ثبت شده قابل ویرایش نیست")

        update_data = data.model_dump(exclude_unset=True)
        line_items = update_data.pop("lines", None)
        if "journal_date" in update_data and update_data["journal_date"]:
            update_data["journal_date"] = to_gregorian(update_data["journal_date"])

        for key, value in update_data.items():
            setattr(journal, key, value)

        if line_items is not None:
            db.query(JournalLine).filter(JournalLine.journal_id == journal.id).delete(synchronize_session=False)
            db.flush()
            lines = [JournalEntryService._build_line(journal.id, JournalLineCreate(**line_data)) for line_data in line_items]
            JournalEntryService._validate_balanced_lines(lines)
            db.add_all(lines)

        db.commit()
        db.refresh(journal)
        return journal

    @staticmethod
    def post(db: Session, journal_id: int) -> JournalEntry | None:
        journal = JournalEntryService.get_by_id(db, journal_id)
        if not journal:
            return None
        if journal.status == JournalStatus.POSTED:
            raise ValueError("سند قبلاً ثبت شده است")

        active_lines = [line for line in journal.lines if not line.is_deleted]
        JournalEntryService._validate_balanced_lines(active_lines)
        journal.status = JournalStatus.POSTED
        journal.posted_at = datetime.utcnow()
        db.commit()
        db.refresh(journal)
        return journal

    @staticmethod
    def delete(db: Session, journal_id: int) -> bool:
        journal = JournalEntryService.get_by_id(db, journal_id)
        if not journal:
            return False
        if journal.status == JournalStatus.POSTED:
            raise ValueError("سند ثبت شده قابل حذف نیست")
        journal.is_deleted = True
        db.commit()
        return True
