from datetime import date

from sqlalchemy.orm import Session

from app.models.account import Account, AccountType
from app.models.bank_account import BankAccount
from app.models.contract import Contract
from app.models.customer import Customer
from app.models.project import Project
from app.models.receipt import PaymentMethod, Receipt, ReceiptStatus
from app.schemas.journal_entry import JournalEntryCreate, JournalLineCreate
from app.schemas.receipt import ReceiptCreate, ReceiptUpdate
from app.services.document_sequence_service import DocumentSequenceService
from app.services.journal_entry_service import JournalEntryService
from app.utils.jalali import to_jalali


class ReceiptService:
    @staticmethod
    def _validate_receipt_data(db: Session, data: ReceiptCreate | ReceiptUpdate, receipt: Receipt | None = None) -> None:
        values = data.model_dump(exclude_unset=True)
        customer_id = values.get("customer_id", receipt.customer_id if receipt else None)
        project_id = values.get("project_id", receipt.project_id if receipt else None)
        contract_id = values.get("contract_id", receipt.contract_id if receipt else None)
        payment_method = values.get("payment_method", receipt.payment_method if receipt else None)
        bank_account_id = values.get("bank_account_id", receipt.bank_account_id if receipt else None)
        cheque_no = values.get("cheque_no", receipt.cheque_no if receipt else None)
        cheque_due_date = values.get("cheque_due_date", receipt.cheque_due_date if receipt else None)
        amount = values.get("amount", receipt.amount if receipt else None)

        if "status" in values:
            raise ValueError("وضعیت دریافت فقط از طریق عملیات تأیید یا ابطال تغییر می‌کند")
        if not amount or amount <= 0:
            raise ValueError("مبلغ دریافت باید بزرگ‌تر از صفر باشد")
        if not db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first():
            raise ValueError("عضو انتخاب‌شده معتبر نیست")
        if not db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first():
            raise ValueError("پروژه انتخاب‌شده معتبر نیست")
        if contract_id:
            contract = db.query(Contract).filter(Contract.id == contract_id, Contract.is_deleted == False).first()
            if not contract or contract.project_member.customer_id != customer_id or contract.project_member.project_id != project_id:
                raise ValueError("قرارداد باید متعلق به عضو و پروژه انتخاب‌شده باشد")
        if payment_method in (PaymentMethod.TRANSFER, PaymentMethod.POS) and not bank_account_id:
            raise ValueError("برای انتقال بانکی یا کارتخوان انتخاب حساب بانکی الزامی است")
        if bank_account_id and not db.query(BankAccount).filter(BankAccount.id == bank_account_id, BankAccount.is_deleted == False, BankAccount.is_active == True).first():
            raise ValueError("حساب بانکی انتخاب‌شده معتبر یا فعال نیست")
        if payment_method == PaymentMethod.CHEQUE and (not cheque_no or not cheque_due_date):
            raise ValueError("برای چک، شماره چک و تاریخ سررسید الزامی است")

    @staticmethod
    def create(db: Session, data: ReceiptCreate) -> Receipt:
        ReceiptService._validate_receipt_data(db, data)
        receipt_no = DocumentSequenceService.get_next_receipt_number(db)
        values = data.model_dump()
        values.pop("status", None)
        values["status"] = ReceiptStatus.DRAFT
        receipt = Receipt(receipt_no=receipt_no, **values)
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def get_by_id(db: Session, receipt_id: int) -> Receipt | None:
        return db.query(Receipt).filter(Receipt.id == receipt_id, Receipt.is_deleted == False).first()

    @staticmethod
    def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(Receipt).filter(Receipt.is_deleted == False)
        if customer_id:
            query = query.filter(Receipt.customer_id == customer_id)
        if project_id:
            query = query.filter(Receipt.project_id == project_id)
        return query.order_by(Receipt.receipt_date.desc(), Receipt.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, receipt_id: int, data: ReceiptUpdate) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return None
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("دریافت تأییدشده یا لغوشده قابل ویرایش نیست؛ سند اصلاحی ثبت کنید")
        ReceiptService._validate_receipt_data(db, data, receipt)
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
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("دریافت تأییدشده یا لغوشده قابل حذف نیست")
        receipt.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def _get_or_create_account(db: Session, account_type: AccountType, code: str, name: str) -> Account:
        account = db.query(Account).filter(Account.account_code == code, Account.is_deleted == False).first()
        if account:
            return account
        account = Account(account_code=code, account_name=name, account_type=account_type, is_active=True)
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
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("فقط دریافت پیش‌نویس قابل تأیید است")

        if receipt.payment_method == PaymentMethod.CASH:
            debit_account = ReceiptService._get_or_create_account(db, AccountType.CASH, "1100", "صندوق")
        elif receipt.payment_method == PaymentMethod.CHEQUE:
            debit_account = ReceiptService._get_or_create_account(db, AccountType.TREASURY, "1400", "اسناد دریافتنی")
        else:
            debit_account = ReceiptService._get_or_create_account(db, AccountType.BANK, "1200", "بانک")
        credit_account = ReceiptService._get_or_create_account(
            db, AccountType.SUSPENSE if receipt.payment_method == PaymentMethod.CHEQUE else AccountType.MEMBER,
            "1500" if receipt.payment_method == PaymentMethod.CHEQUE else "1300",
            "چک‌های در جریان وصول" if receipt.payment_method == PaymentMethod.CHEQUE else "حساب اعضا",
        )
        description = receipt.description or f"ثبت دریافت {receipt.receipt_no}"

        try:
            journal = JournalEntryService.create(
                db,
                JournalEntryCreate(journal_date=to_jalali(receipt.receipt_date), status="POSTED", description=description,
                                   reference_type="RECEIPT", reference_id=receipt.id,
                                   lines=[JournalLineCreate(account_id=debit_account.id, debit=receipt.amount, description=description),
                                          JournalLineCreate(account_id=credit_account.id, credit=receipt.amount, description=description)]),
                commit=False,
            )
            receipt.status = ReceiptStatus.CONFIRMED
            receipt.confirmed_at = date.today()
            if receipt.payment_method == PaymentMethod.CHEQUE:
                receipt.cheque_status = "PENDING_COLLECTION"
            else:
                ReceiptService.allocate_to_obligations(db, receipt)
            receipt.journal_entry_id = journal.id
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(receipt)
        return receipt

    @staticmethod
    def allocate_to_obligations(db: Session, receipt: Receipt) -> None:
        """Allocate a financially effective receipt to the oldest open obligations."""
        from app.models.financial_obligation import FinancialObligation, ObligationStatus
        from app.models.receipt_allocation import ReceiptAllocation
        remaining = receipt.amount
        obligations = db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == receipt.customer_id, FinancialObligation.project_id == receipt.project_id,
            FinancialObligation.is_deleted == False, FinancialObligation.status != ObligationStatus.CANCELLED,
        ).order_by(FinancialObligation.due_date.nulls_last(), FinancialObligation.id).all()
        for obligation in obligations:
            if remaining <= 0: break
            open_amount = obligation.amount - (obligation.paid_amount or 0)
            if open_amount <= 0: continue
            amount = min(remaining, open_amount)
            db.add(ReceiptAllocation(receipt_id=receipt.id, obligation_id=obligation.id, allocated_amount=amount, allocated_at=date.today()))
            obligation.paid_amount = (obligation.paid_amount or 0) + amount
            obligation.status = ObligationStatus.PAID if obligation.paid_amount >= obligation.amount else ObligationStatus.PARTIAL
            remaining -= amount

    @staticmethod
    def collect_cheque(db: Session, receipt_id: int) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt: return None
        if receipt.payment_method != PaymentMethod.CHEQUE or receipt.cheque_status != "PENDING_COLLECTION":
            raise ValueError("فقط چک در جریان وصول قابل وصول است")
        from app.models.journal_entry import JournalEntry
        if db.query(JournalEntry).filter(JournalEntry.reference_type == "CHEQUE_COLLECTION", JournalEntry.reference_id == receipt.id, JournalEntry.is_deleted == False).first():
            return receipt
        treasury = ReceiptService._get_or_create_account(db, AccountType.TREASURY, "1400", "اسناد دریافتنی")
        bank = ReceiptService._get_or_create_account(db, AccountType.BANK, "1200", "بانک")
        suspense = ReceiptService._get_or_create_account(db, AccountType.SUSPENSE, "1500", "چک‌های در جریان وصول")
        member = ReceiptService._get_or_create_account(db, AccountType.MEMBER, "1300", "حساب اعضا")
        try:
            JournalEntryService.create(db, JournalEntryCreate(journal_date=to_jalali(receipt.receipt_date), status="POSTED", reference_type="CHEQUE_COLLECTION", reference_id=receipt.id, description=f"وصول چک {receipt.cheque_no}", lines=[JournalLineCreate(account_id=bank.id, debit=receipt.amount), JournalLineCreate(account_id=treasury.id, credit=receipt.amount), JournalLineCreate(account_id=suspense.id, debit=receipt.amount), JournalLineCreate(account_id=member.id, credit=receipt.amount)]), commit=False)
            receipt.cheque_status = "COLLECTED"; receipt.cheque_collected_at = date.today(); ReceiptService.allocate_to_obligations(db, receipt); db.commit()
        except Exception: db.rollback(); raise
        db.refresh(receipt); return receipt

    @staticmethod
    def return_cheque(db: Session, receipt_id: int, reason: str | None = None) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt: return None
        if receipt.payment_method != PaymentMethod.CHEQUE or receipt.cheque_status != "PENDING_COLLECTION":
            raise ValueError("فقط چک در جریان وصول قابل برگشت است")
        treasury = ReceiptService._get_or_create_account(db, AccountType.TREASURY, "1400", "اسناد دریافتنی")
        suspense = ReceiptService._get_or_create_account(db, AccountType.SUSPENSE, "1500", "چک‌های در جریان وصول")
        try:
            JournalEntryService.create(db, JournalEntryCreate(journal_date=to_jalali(receipt.receipt_date), status="POSTED", reference_type="CHEQUE_RETURN", reference_id=receipt.id, description=reason or f"برگشت چک {receipt.cheque_no}", lines=[JournalLineCreate(account_id=suspense.id, debit=receipt.amount), JournalLineCreate(account_id=treasury.id, credit=receipt.amount)]), commit=False)
            receipt.cheque_status = "RETURNED"; receipt.cheque_returned_at = date.today(); receipt.cheque_return_reason = reason; db.commit()
        except Exception: db.rollback(); raise
        db.refresh(receipt); return receipt

    @staticmethod
    def cancel(db: Session, receipt_id: int) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt: return None
        if receipt.status == ReceiptStatus.CANCELLED: return receipt
        if receipt.status != ReceiptStatus.CONFIRMED: raise ValueError("فقط دریافت تأییدشده قابل ابطال است")
        debit = ReceiptService._get_or_create_account(db, AccountType.MEMBER, "1300", "حساب اعضا")
        if receipt.payment_method == PaymentMethod.CHEQUE: credit = ReceiptService._get_or_create_account(db, AccountType.TREASURY, "1400", "اسناد دریافتنی")
        elif receipt.payment_method == PaymentMethod.CASH: credit = ReceiptService._get_or_create_account(db, AccountType.CASH, "1100", "صندوق")
        else: credit = ReceiptService._get_or_create_account(db, AccountType.BANK, "1200", "بانک")
        try:
            JournalEntryService.create(db, JournalEntryCreate(journal_date=to_jalali(receipt.receipt_date), status="POSTED", reference_type="RECEIPT_REVERSAL", reference_id=receipt.id, description=f"ابطال دریافت {receipt.receipt_no}", lines=[JournalLineCreate(account_id=debit.id, debit=receipt.amount), JournalLineCreate(account_id=credit.id, credit=receipt.amount)]), commit=False)
            from app.models.receipt_allocation import ReceiptAllocation
            from app.models.financial_obligation import ObligationStatus
            for allocation in db.query(ReceiptAllocation).filter(ReceiptAllocation.receipt_id == receipt.id).all():
                allocation.obligation.paid_amount -= allocation.allocated_amount
                allocation.obligation.status = ObligationStatus.PENDING if allocation.obligation.paid_amount == 0 else ObligationStatus.PARTIAL
                db.delete(allocation)
            receipt.status=ReceiptStatus.CANCELLED; db.commit()
        except Exception: db.rollback(); raise
        db.refresh(receipt); return receipt
