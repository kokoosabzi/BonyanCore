from datetime import datetime

from sqlalchemy.orm import Session

from app.models.bank_account import BankAccount
from app.models.contract import Contract
from app.models.financial_credit import (
    CreditStatus,
    CreditType,
    FinancialCredit,
)
from app.models.financial_obligation import (
    FinancialObligation,
    ObligationStatus,
)
from app.models.journal_entry import JournalEntryType
from app.models.journal_line import DebitCredit
from app.models.project_member import ProjectMember
from app.models.receipt import PaymentMethod, Receipt, ReceiptStatus
from app.models.receipt_allocation import ReceiptAllocation
from app.schemas.receipt import (
    ReceiptAllocationInput,
    ReceiptCreate,
    ReceiptUpdate,
)
from app.services.accounting_service import AccountingService
from app.services.document_sequence_service import DocumentSequenceService
from app.utils.amount_words import amount_in_words


class ReceiptService:
    @staticmethod
    def _resolve_membership(
        db: Session,
        customer_id: int,
        project_id: int,
        project_member_id: int | None,
    ) -> ProjectMember:
        query = db.query(ProjectMember).filter(
            ProjectMember.customer_id == customer_id,
            ProjectMember.project_id == project_id,
            ProjectMember.is_deleted.is_(False),
        )
        if project_member_id:
            query = query.filter(ProjectMember.id == project_member_id)
        membership = query.first()
        if not membership:
            raise ValueError("مشتری عضو پروژه انتخاب‌شده نیست")
        return membership

    @staticmethod
    def _validate_contract(
        db: Session,
        contract_id: int | None,
        membership_id: int,
    ) -> None:
        if not contract_id:
            return
        contract = db.query(Contract).filter(
            Contract.id == contract_id,
            Contract.is_deleted.is_(False),
        ).first()
        if not contract or contract.project_member_id != membership_id:
            raise ValueError("قرارداد انتخاب‌شده با عضویت مشتری مطابقت ندارد")

    @staticmethod
    def _validate_payment_details(
        db: Session,
        payment_method: PaymentMethod,
        bank_account_id: int | None,
        cheque_no: str | None,
        cheque_due_date,
    ) -> None:
        if payment_method == PaymentMethod.CHEQUE:
            if not cheque_no or not cheque_due_date:
                raise ValueError("شماره و تاریخ سررسید چک الزامی است")
        if payment_method in {
            PaymentMethod.DEPOSIT_SLIP,
            PaymentMethod.TRANSFER,
            PaymentMethod.POS,
        } and not bank_account_id:
            raise ValueError("انتخاب حساب بانکی برای این روش پرداخت الزامی است")
        if bank_account_id:
            account = db.query(BankAccount).filter(
                BankAccount.id == bank_account_id,
                BankAccount.is_active.is_(True),
                BankAccount.is_deleted.is_(False),
            ).first()
            if not account:
                raise ValueError("حساب بانکی انتخاب‌شده معتبر نیست")

    @staticmethod
    def create(
        db: Session,
        data: ReceiptCreate,
        operator_id: int | None = None,
    ) -> Receipt:
        try:
            membership = ReceiptService._resolve_membership(
                db,
                data.customer_id,
                data.project_id,
                data.project_member_id,
            )
            ReceiptService._validate_contract(
                db,
                data.contract_id,
                membership.id,
            )
            payment_method = PaymentMethod(data.payment_method.value)
            ReceiptService._validate_payment_details(
                db,
                payment_method,
                data.bank_account_id,
                data.cheque_no,
                data.cheque_due_date,
            )

            payload = data.model_dump(
                exclude={"status", "project_member_id", "payment_method"}
            )
            receipt = Receipt(
                receipt_no=DocumentSequenceService.get_next_receipt_number(db),
                project_member_id=membership.id,
                payment_method=payment_method,
                status=ReceiptStatus.DRAFT,
                amount_in_words=amount_in_words(data.amount),
                operator_id=operator_id,
                **payload,
            )
            db.add(receipt)
            db.commit()
            db.refresh(receipt)
            return receipt
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(db: Session, receipt_id: int) -> Receipt | None:
        return db.query(Receipt).filter(
            Receipt.id == receipt_id,
            Receipt.is_deleted.is_(False),
        ).first()

    @staticmethod
    def get_all(
        db: Session,
        customer_id: int | None = None,
        project_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ):
        query = db.query(Receipt).filter(Receipt.is_deleted.is_(False))
        if customer_id:
            query = query.filter(Receipt.customer_id == customer_id)
        if project_id:
            query = query.filter(Receipt.project_id == project_id)
        return query.order_by(Receipt.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        receipt_id: int,
        data: ReceiptUpdate,
    ) -> Receipt | None:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return None
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("فقط فیش پیش‌نویس قابل ویرایش است")

        try:
            update_data = data.model_dump(exclude_unset=True)
            if "payment_method" in update_data:
                update_data["payment_method"] = PaymentMethod(
                    update_data["payment_method"].value
                )
            payment_method = update_data.get(
                "payment_method",
                receipt.payment_method,
            )
            bank_account_id = update_data.get(
                "bank_account_id",
                receipt.bank_account_id,
            )
            cheque_no = update_data.get("cheque_no", receipt.cheque_no)
            cheque_due_date = update_data.get(
                "cheque_due_date",
                receipt.cheque_due_date,
            )
            ReceiptService._validate_payment_details(
                db,
                payment_method,
                bank_account_id,
                cheque_no,
                cheque_due_date,
            )
            for key, value in update_data.items():
                setattr(receipt, key, value)
            if "amount" in update_data:
                receipt.amount_in_words = amount_in_words(receipt.amount)
            db.commit()
            db.refresh(receipt)
            return receipt
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete(db: Session, receipt_id: int) -> bool:
        receipt = ReceiptService.get_by_id(db, receipt_id)
        if not receipt:
            return False
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("فیش تأییدشده یا لغوشده قابل حذف نیست")
        receipt.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def _build_allocations(
        db: Session,
        receipt: Receipt,
        requested: list[ReceiptAllocationInput] | None,
    ) -> list[tuple[FinancialObligation, int]]:
        allocations: list[tuple[FinancialObligation, int]] = []
        if requested:
            seen_ids: set[int] = set()
            for item in requested:
                if item.obligation_id in seen_ids:
                    raise ValueError("یک بدهی بیش از یک بار در تخصیص‌ها تکرار شده است")
                seen_ids.add(item.obligation_id)
                obligation = db.query(FinancialObligation).filter(
                    FinancialObligation.id == item.obligation_id,
                    FinancialObligation.customer_id == receipt.customer_id,
                    FinancialObligation.project_id == receipt.project_id,
                    FinancialObligation.is_deleted.is_(False),
                    FinancialObligation.status.in_(
                        [ObligationStatus.PENDING, ObligationStatus.PARTIAL]
                    ),
                ).with_for_update().first()
                if not obligation:
                    raise ValueError("بدهی انتخاب‌شده معتبر یا قابل پرداخت نیست")
                outstanding = obligation.amount - (obligation.paid_amount or 0)
                if item.amount > outstanding:
                    raise ValueError(
                        f"مبلغ تخصیص برای بدهی {obligation.obligation_no} بیشتر از مانده است"
                    )
                allocations.append((obligation, item.amount))
        else:
            remaining = receipt.amount
            obligations = db.query(FinancialObligation).filter(
                FinancialObligation.customer_id == receipt.customer_id,
                FinancialObligation.project_id == receipt.project_id,
                FinancialObligation.is_deleted.is_(False),
                FinancialObligation.status.in_(
                    [ObligationStatus.PENDING, ObligationStatus.PARTIAL]
                ),
            ).order_by(
                FinancialObligation.due_date.is_(None),
                FinancialObligation.due_date,
                FinancialObligation.id,
            ).with_for_update().all()
            for obligation in obligations:
                if remaining <= 0:
                    break
                outstanding = obligation.amount - (obligation.paid_amount or 0)
                if outstanding <= 0:
                    continue
                allocated = min(remaining, outstanding)
                allocations.append((obligation, allocated))
                remaining -= allocated

        if sum(amount for _, amount in allocations) > receipt.amount:
            raise ValueError("جمع تخصیص‌ها نمی‌تواند بیشتر از مبلغ فیش باشد")
        return allocations

    @staticmethod
    def confirm(
        db: Session,
        receipt_id: int,
        confirmed_by: int,
        username: str,
        allocations: list[ReceiptAllocationInput] | None = None,
    ) -> Receipt | None:
        receipt = db.query(Receipt).filter(
            Receipt.id == receipt_id,
            Receipt.is_deleted.is_(False),
        ).with_for_update().first()
        if not receipt:
            return None
        if receipt.status != ReceiptStatus.DRAFT:
            raise ValueError("فقط فیش پیش‌نویس قابل تأیید است")
        if receipt.financial_credit or receipt.journal_entry_id:
            raise ValueError("فرایند مالی این فیش قبلاً ثبت شده است")

        try:
            ReceiptService._validate_payment_details(
                db,
                receipt.payment_method,
                receipt.bank_account_id,
                receipt.cheque_no,
                receipt.cheque_due_date,
            )
            requested_allocations = ReceiptService._build_allocations(
                db,
                receipt,
                allocations,
            )

            debit_account = AccountingService.receipt_debit_account(
                db,
                receipt.payment_method,
                receipt.bank_account_id,
            )
            member_account = AccountingService.member_receivable_account(db)
            journal = AccountingService.create_posted_journal(
                db,
                journal_date=receipt.receipt_date,
                entry_type=JournalEntryType.RECEIPT,
                description=f"ثبت دریافت {receipt.receipt_no}",
                reference_type="RECEIPT",
                reference_id=receipt.id,
                posted_by=username,
                lines=[
                    (
                        debit_account,
                        DebitCredit.DEBIT,
                        receipt.amount,
                        f"دریافت فیش {receipt.receipt_no}",
                    ),
                    (
                        member_account,
                        DebitCredit.CREDIT,
                        receipt.amount,
                        f"کاهش حساب دریافتنی بابت {receipt.receipt_no}",
                    ),
                ],
            )

            credit = FinancialCredit(
                credit_no=DocumentSequenceService.get_next_credit_number(db),
                customer_id=receipt.customer_id,
                project_id=receipt.project_id,
                contract_id=receipt.contract_id,
                credit_type=CreditType.PAYMENT,
                amount=receipt.amount,
                status=CreditStatus.APPROVED,
                credit_date=receipt.receipt_date,
                description=receipt.description or f"دریافت {receipt.receipt_no}",
                reference_id=receipt.receipt_no,
                bank_account_id=receipt.bank_account_id,
                cheque_no=receipt.cheque_no,
                receipt_id=receipt.id,
                journal_entry_id=journal.id,
            )
            db.add(credit)

            for obligation, allocated_amount in requested_allocations:
                db.add(
                    ReceiptAllocation(
                        receipt_id=receipt.id,
                        obligation_id=obligation.id,
                        amount=allocated_amount,
                        description=f"تخصیص فیش {receipt.receipt_no}",
                    )
                )
                obligation.paid_amount = (
                    obligation.paid_amount or 0
                ) + allocated_amount
                obligation.status = (
                    ObligationStatus.PAID
                    if obligation.paid_amount >= obligation.amount
                    else ObligationStatus.PARTIAL
                )

            receipt.status = ReceiptStatus.CONFIRMED
            receipt.confirmed_by = confirmed_by
            receipt.confirmed_at = datetime.now()
            receipt.journal_entry_id = journal.id
            db.commit()
            db.refresh(receipt)
            return receipt
        except Exception:
            db.rollback()
            raise
