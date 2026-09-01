from datetime import date
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus
from app.models.account import Account, AccountType
from app.schemas.payment import PaymentCreate
from app.schemas.journal_entry import JournalEntryCreate, JournalLineCreate
from app.services.document_sequence_service import DocumentSequenceService
from app.services.journal_entry_service import JournalEntryService
from app.utils.jalali import to_jalali

class PaymentService:
    @staticmethod
    def create(db: Session, data: PaymentCreate) -> Payment:
        payment = Payment(payment_no=DocumentSequenceService.get_next_payment_number(db), **data.model_dump())
        db.add(payment); db.commit(); db.refresh(payment); return payment
    @staticmethod
    def get_by_id(db, payment_id):
        return db.query(Payment).filter(Payment.id == payment_id, Payment.is_deleted == False).first()
    @staticmethod
    def confirm(db: Session, payment_id: int) -> Payment | None:
        payment = PaymentService.get_by_id(db, payment_id)
        if not payment: return None
        if payment.status == PaymentStatus.CONFIRMED: return payment
        if payment.status != PaymentStatus.DRAFT: raise ValueError("فقط پرداخت پیش‌نویس قابل تأیید است")
        expense = PaymentService._account(db, AccountType.PROJECT, "2100", "هزینه پروژه")
        bank = PaymentService._account(db, AccountType.BANK, "1200", "بانک")
        try:
            journal = JournalEntryService.create(db, JournalEntryCreate(
                journal_date=to_jalali(payment.payment_date), status="POSTED", reference_type="PAYMENT", reference_id=payment.id,
                description=payment.description or f"پرداخت {payment.payment_no}", lines=[
                    JournalLineCreate(account_id=expense.id, debit=payment.amount, description=payment.description),
                    JournalLineCreate(account_id=bank.id, credit=payment.amount, description=payment.description),
                ]), commit=False)
            payment.status=PaymentStatus.CONFIRMED; payment.confirmed_at=date.today(); payment.journal_entry_id=journal.id; db.commit()
        except Exception: db.rollback(); raise
        db.refresh(payment); return payment
    @staticmethod
    def _account(db, account_type, code, name):
        account=db.query(Account).filter(Account.account_code==code, Account.is_deleted==False).first()
        if not account: account=Account(account_code=code, account_name=name, account_type=account_type, is_active=True); db.add(account); db.flush()
        return account

    @staticmethod
    def cancel(db: Session, payment_id: int) -> Payment | None:
        payment = PaymentService.get_by_id(db, payment_id)
        if not payment: return None
        if payment.status == PaymentStatus.CANCELLED: return payment
        if payment.status != PaymentStatus.CONFIRMED: raise ValueError("فقط پرداخت تأییدشده قابل ابطال است")
        expense = PaymentService._account(db, AccountType.PROJECT, "2100", "هزینه پروژه"); bank = PaymentService._account(db, AccountType.BANK, "1200", "بانک")
        try:
            JournalEntryService.create(db, JournalEntryCreate(journal_date=to_jalali(payment.payment_date), status="POSTED", reference_type="PAYMENT_REVERSAL", reference_id=payment.id, description=f"ابطال پرداخت {payment.payment_no}", lines=[JournalLineCreate(account_id=bank.id, debit=payment.amount), JournalLineCreate(account_id=expense.id, credit=payment.amount)]), commit=False)
            payment.status=PaymentStatus.CANCELLED; db.commit()
        except Exception: db.rollback(); raise
        db.refresh(payment); return payment
