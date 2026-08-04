from sqlalchemy.orm import Session

from app.models.financial_credit import (
    CreditStatus,
    CreditType,
    FinancialCredit,
)
from app.models.journal_entry import JournalEntryType
from app.models.journal_line import DebitCredit
from app.schemas.financial_credit import (
    FinancialCreditCreate,
    FinancialCreditUpdate,
)
from app.services.accounting_service import AccountingService
from app.services.document_sequence_service import DocumentSequenceService


class FinancialCreditService:
    @staticmethod
    def create(
        db: Session,
        data: FinancialCreditCreate,
        posted_by: str = "system",
    ) -> FinancialCredit:
        try:
            payload = data.model_dump(exclude={"credit_type", "status"})
            credit = FinancialCredit(
                credit_no=DocumentSequenceService.get_next_credit_number(db),
                credit_type=CreditType(data.credit_type.value),
                status=CreditStatus.APPROVED,
                **payload,
            )
            db.add(credit)
            db.flush()

            project_account = AccountingService.project_income_account(db)
            member_account = AccountingService.member_receivable_account(db)
            journal = AccountingService.create_posted_journal(
                db,
                journal_date=credit.credit_date,
                entry_type=JournalEntryType.CREDIT,
                description=f"ثبت اعتبار {credit.credit_no}",
                reference_type="FINANCIAL_CREDIT",
                reference_id=credit.id,
                posted_by=posted_by,
                lines=[
                    (
                        project_account,
                        DebitCredit.DEBIT,
                        credit.amount,
                        f"ثبت اعتبار بابت {credit.credit_no}",
                    ),
                    (
                        member_account,
                        DebitCredit.CREDIT,
                        credit.amount,
                        f"بستانکار شدن عضو بابت {credit.credit_no}",
                    ),
                ],
            )
            credit.journal_entry_id = journal.id
            db.commit()
            db.refresh(credit)
            return credit
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(db: Session, credit_id: int) -> FinancialCredit | None:
        return db.query(FinancialCredit).filter(
            FinancialCredit.id == credit_id,
            FinancialCredit.is_deleted.is_(False),
        ).first()

    @staticmethod
    def get_by_customer(db: Session, customer_id: int):
        return db.query(FinancialCredit).filter(
            FinancialCredit.customer_id == customer_id,
            FinancialCredit.is_deleted.is_(False),
        ).all()

    @staticmethod
    def get_by_project(db: Session, project_id: int):
        return db.query(FinancialCredit).filter(
            FinancialCredit.project_id == project_id,
            FinancialCredit.is_deleted.is_(False),
        ).all()

    @staticmethod
    def get_all(
        db: Session,
        customer_id: int | None = None,
        project_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ):
        query = db.query(FinancialCredit).filter(
            FinancialCredit.is_deleted.is_(False)
        )
        if customer_id:
            query = query.filter(FinancialCredit.customer_id == customer_id)
        if project_id:
            query = query.filter(FinancialCredit.project_id == project_id)
        return query.order_by(
            FinancialCredit.id.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        credit_id: int,
        data: FinancialCreditUpdate,
    ) -> FinancialCredit | None:
        credit = FinancialCreditService.get_by_id(db, credit_id)
        if not credit:
            return None
        if credit.journal_entry_id or credit.receipt_id:
            raise ValueError(
                "اعتبار ثبت‌شده در حسابداری قابل ویرایش نیست؛ از سند اصلاحی استفاده کنید"
            )
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(credit, key, value)
        db.commit()
        db.refresh(credit)
        return credit

    @staticmethod
    def delete(db: Session, credit_id: int) -> bool:
        credit = FinancialCreditService.get_by_id(db, credit_id)
        if not credit:
            return False
        if credit.journal_entry_id or credit.receipt_id:
            raise ValueError(
                "اعتبار ثبت‌شده در حسابداری قابل حذف نیست؛ از سند اصلاحی استفاده کنید"
            )
        credit.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def get_total_credits(db: Session, customer_id: int) -> int:
        total = db.query(FinancialCredit).filter(
            FinancialCredit.customer_id == customer_id,
            FinancialCredit.is_deleted.is_(False),
            FinancialCredit.status != CreditStatus.REVERSED,
        ).with_entities(FinancialCredit.amount).all()
        return sum(row[0] for row in total) if total else 0

    @staticmethod
    def get_net_balance(db: Session, customer_id: int) -> int:
        from app.services.financial_obligation_service import (
            FinancialObligationService,
        )

        total_obligations = FinancialObligationService.get_total_obligations(
            db,
            customer_id,
        )
        total_credits = FinancialCreditService.get_total_credits(
            db,
            customer_id,
        )
        return total_obligations - total_credits
