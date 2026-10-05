from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.account import Account, AccountType
from app.models.journal_entry import (
    JournalEntry,
    JournalEntryType,
    JournalStatus,
)
from app.models.journal_line import DebitCredit, JournalLine
from app.models.receipt import PaymentMethod
from app.services.document_sequence_service import DocumentSequenceService


class AccountingService:
    @staticmethod
    def get_or_create_control_account(
        db: Session,
        code: str,
        name: str,
        account_type: AccountType,
    ) -> Account:
        account = db.query(Account).filter(
            Account.account_code == code,
            Account.is_deleted.is_(False),
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
    def member_receivable_account(db: Session) -> Account:
        return AccountingService.get_or_create_control_account(
            db,
            "MEMBER-RECEIVABLE",
            "حساب دریافتنی اعضا",
            AccountType.MEMBER,
        )

    @staticmethod
    def project_income_account(db: Session) -> Account:
        return AccountingService.get_or_create_control_account(
            db,
            "PROJECT-INCOME",
            "درآمد و مطالبات پروژه",
            AccountType.PROJECT,
        )

    @staticmethod
    def receipt_debit_account(
        db: Session,
        payment_method: PaymentMethod,
        bank_account_id: int | None,
    ) -> Account:
        if payment_method == PaymentMethod.CASH:
            return AccountingService.get_or_create_control_account(
                db,
                "CASH-ON-HAND",
                "صندوق",
                AccountType.CASH,
            )
        if payment_method == PaymentMethod.CHEQUE:
            return AccountingService.get_or_create_control_account(
                db,
                "CHEQUES-IN-HAND",
                "اسناد دریافتنی",
                AccountType.TREASURY,
            )
        if bank_account_id is None:
            return AccountingService.get_or_create_control_account(
                db,
                "UNIDENTIFIED-RECEIPT",
                "وجوه دریافتنی در انتظار تعیین تکلیف",
                AccountType.SUSPENSE,
            )
        return AccountingService.get_or_create_control_account(
            db,
            f"BANK-{bank_account_id}",
            f"حساب بانکی شماره {bank_account_id}",
            AccountType.BANK,
        )

    @staticmethod
    def create_posted_journal(
        db: Session,
        *,
        journal_date: date,
        entry_type: JournalEntryType,
        description: str,
        reference_type: str,
        reference_id: int,
        posted_by: str,
        lines: list[tuple[Account, DebitCredit, int, str]],
    ) -> JournalEntry:
        total_debit = sum(
            amount
            for _, side, amount, _ in lines
            if side == DebitCredit.DEBIT
        )
        total_credit = sum(
            amount
            for _, side, amount, _ in lines
            if side == DebitCredit.CREDIT
        )
        if total_debit <= 0 or total_debit != total_credit:
            raise ValueError("سند حسابداری باید متوازن و دارای مبلغ مثبت باشد")

        journal = JournalEntry(
            journal_no=DocumentSequenceService.get_next_journal_number(db),
            journal_date=journal_date,
            entry_type=entry_type,
            status=JournalStatus.POSTED,
            description=description,
            posted_by=posted_by,
            posted_at=datetime.now(),
            reference_type=reference_type,
            reference_id=reference_id,
        )
        db.add(journal)
        db.flush()
        for account, side, amount, line_description in lines:
            db.add(
                JournalLine(
                    journal_id=journal.id,
                    account_id=account.id,
                    debit_credit=side,
                    amount=amount,
                    description=line_description,
                )
            )
        db.flush()
        return journal
