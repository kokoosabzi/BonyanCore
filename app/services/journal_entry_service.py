from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.journal_entry import JournalEntry, JournalStatus
from app.models.journal_line import JournalLine, DebitCredit
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryUpdate, JournalLineCreate
from app.services.document_sequence_service import DocumentSequenceService

class JournalEntryService:
    @staticmethod
    def create(db: Session, data: JournalEntryCreate) -> JournalEntry:
        journal_no = DocumentSequenceService.get_next_journal_number(db)
        
        # تبدیل تاریخ شمسی به میلادی (ساده)
        from app.utils.jalali import to_gregorian
        journal_date = to_gregorian(data.journal_date)
        
        journal = JournalEntry(
            journal_no=journal_no,
            journal_date=journal_date,
            status=data.status or JournalStatus.DRAFT,
            description=data.description,
            reference_type=data.reference_type,
            reference_id=data.reference_id
        )
        db.add(journal)
        db.flush()
        
        total_debit = 0
        total_credit = 0
        created_lines = 0
        
        for line_data in data.lines:
            debit = line_data.debit or 0
            credit = line_data.credit or 0
            if debit > 0 and credit > 0:
                db.rollback()
                raise ValueError("هر ردیف فقط می‌تواند بدهکار یا بستانکار باشد")
            if debit > 0:
                line = JournalLine(
                    journal_id=journal.id,
                    account_id=line_data.account_id,
                    debit_credit=DebitCredit.DEBIT,
                    amount=debit,
                    description=line_data.description,
                    analytic_account_id=line_data.analytic_account_id
                )
                db.add(line)
                total_debit += debit
                created_lines += 1
            elif credit > 0:
                line = JournalLine(
                    journal_id=journal.id,
                    account_id=line_data.account_id,
                    debit_credit=DebitCredit.CREDIT,
                    amount=credit,
                    description=line_data.description,
                    analytic_account_id=line_data.analytic_account_id
                )
                db.add(line)
                total_credit += credit
                created_lines += 1

        if created_lines < 2:
            db.rollback()
            raise ValueError("حداقل دو ردیف معتبر برای سند حسابداری لازم است")
        
        if total_debit != total_credit:
            db.rollback()
            raise ValueError("جمع بدهکار و بستانکار باید برابر باشد")
        
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
        if "journal_date" in update_data and update_data["journal_date"]:
            from app.utils.jalali import to_gregorian
            update_data["journal_date"] = to_gregorian(update_data["journal_date"])
        for key, value in update_data.items():
            setattr(journal, key, value)
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
        journal.status = JournalStatus.POSTED
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