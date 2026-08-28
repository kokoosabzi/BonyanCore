from sqlalchemy.orm import Session
from app.models.receipt import PaymentMethod, Receipt, ReceiptStatus
from app.models.account import Account, AccountType
from app.schemas.receipt import ReceiptCreate, ReceiptUpdate
from app.services.document_sequence_service import DocumentSequenceService
from app.services.journal_entry_service import JournalEntryService
from app.schemas.journal_entry import JournalEntryCreate, JournalLineCreate
from app.utils.jalali import to_jalali

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
    def _get_or_create_account(db: Session, account_type: AccountType, code: str, name: str) -> Account:
        account = db.query(Account).filter(
            Account.account_code == code,
            Account.is_deleted == False,
        ).first()
        if account:
            return account

        account = Account(
            account_code=code,
            account_name=name,
            account_type=account_type,
            is_active=True,
        )
        db.add(account)
        db.flush()
        return account

    @staticmethod
    def confirm(db: Session, receipt_id: int) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return None
        if receipt.status == ReceiptStatus.CONFIRMED:
            return receipt

        debit_account_type = AccountType.CASH if receipt.payment_method == PaymentMethod.CASH else AccountType.BANK
        debit_account = ReceiptService._get_or_create_account(
            db,
            debit_account_type,
            "1100" if debit_account_type == AccountType.CASH else "1200",
            "صندوق" if debit_account_type == AccountType.CASH else "بانک",
        )
        credit_account = ReceiptService._get_or_create_account(
            db,
            AccountType.MEMBER,
            "1300",
            "حساب اعضا",
        )

        journal = JournalEntryService.create(
            db,
            JournalEntryCreate(
                journal_date=to_jalali(receipt.receipt_date),
                status="POSTED",
                description=receipt.description or f"ثبت دریافت {receipt.receipt_no}",
                reference_type="RECEIPT",
                reference_id=receipt.id,
                lines=[
                    JournalLineCreate(
                        account_id=debit_account.id,
                        debit=receipt.amount,
                        description=receipt.description or f"دریافت {receipt.receipt_no}",
                    ),
                    JournalLineCreate(
                        account_id=credit_account.id,
                        credit=receipt.amount,
                        description=receipt.description or f"دریافت {receipt.receipt_no}",
                    ),
                ],
            ),
        )
        receipt.status = ReceiptStatus.CONFIRMED
        receipt.journal_entry_id = journal.id
        db.commit()
        db.refresh(receipt)
        return receipt
