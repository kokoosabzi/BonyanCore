from datetime import date

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.financial_obligation import (
    FinancialObligation,
    ObligationStatus,
    ObligationType,
)
from app.models.journal_entry import JournalEntryType
from app.models.journal_line import DebitCredit
from app.models.project_member import ProjectMember
from app.schemas.financial_obligation import (
    FinancialObligationCreate,
    FinancialObligationUpdate,
)
from app.services.accounting_service import AccountingService
from app.services.document_sequence_service import DocumentSequenceService


class FinancialObligationService:
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
    def create(
        db: Session,
        data: FinancialObligationCreate,
        posted_by: str = "system",
    ) -> FinancialObligation:
        try:
            membership = FinancialObligationService._resolve_membership(
                db,
                data.customer_id,
                data.project_id,
                data.project_member_id,
            )
            if data.contract_id:
                contract = db.query(Contract).filter(
                    Contract.id == data.contract_id,
                    Contract.is_deleted.is_(False),
                ).first()
                if not contract or contract.project_member_id != membership.id:
                    raise ValueError(
                        "قرارداد انتخاب‌شده با عضویت مشتری مطابقت ندارد"
                    )

            payload = data.model_dump(
                exclude={"project_member_id", "obligation_type"}
            )
            obligation = FinancialObligation(
                obligation_no=DocumentSequenceService.get_next_obligation_number(
                    db
                ),
                project_member_id=membership.id,
                obligation_type=ObligationType(data.obligation_type.value),
                paid_amount=0,
                status=ObligationStatus.PENDING,
                **payload,
            )
            db.add(obligation)
            db.flush()

            member_account = AccountingService.member_receivable_account(db)
            project_account = AccountingService.project_income_account(db)
            journal = AccountingService.create_posted_journal(
                db,
                journal_date=date.today(),
                entry_type=JournalEntryType.DEBIT,
                description=f"ثبت بدهی {obligation.obligation_no}",
                reference_type="FINANCIAL_OBLIGATION",
                reference_id=obligation.id,
                posted_by=posted_by,
                lines=[
                    (
                        member_account,
                        DebitCredit.DEBIT,
                        obligation.amount,
                        f"بدهکار شدن عضو بابت {obligation.obligation_no}",
                    ),
                    (
                        project_account,
                        DebitCredit.CREDIT,
                        obligation.amount,
                        f"مطالبه پروژه بابت {obligation.obligation_no}",
                    ),
                ],
            )
            obligation.journal_entry_id = journal.id
            db.commit()
            db.refresh(obligation)
            return obligation
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(
        db: Session,
        obligation_id: int,
    ) -> FinancialObligation | None:
        return db.query(FinancialObligation).filter(
            FinancialObligation.id == obligation_id,
            FinancialObligation.is_deleted.is_(False),
        ).first()

    @staticmethod
    def get_by_customer(db: Session, customer_id: int):
        return db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == customer_id,
            FinancialObligation.is_deleted.is_(False),
        ).all()

    @staticmethod
    def get_by_project(db: Session, project_id: int):
        return db.query(FinancialObligation).filter(
            FinancialObligation.project_id == project_id,
            FinancialObligation.is_deleted.is_(False),
        ).all()

    @staticmethod
    def get_all(
        db: Session,
        customer_id: int | None = None,
        project_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ):
        query = db.query(FinancialObligation).filter(
            FinancialObligation.is_deleted.is_(False)
        )
        if customer_id:
            query = query.filter(
                FinancialObligation.customer_id == customer_id
            )
        if project_id:
            query = query.filter(FinancialObligation.project_id == project_id)
        return query.order_by(
            FinancialObligation.id.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        obligation_id: int,
        data: FinancialObligationUpdate,
    ) -> FinancialObligation | None:
        obligation = FinancialObligationService.get_by_id(db, obligation_id)
        if not obligation:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obligation, key, value)
        db.commit()
        db.refresh(obligation)
        return obligation

    @staticmethod
    def delete(db: Session, obligation_id: int) -> bool:
        obligation = FinancialObligationService.get_by_id(db, obligation_id)
        if not obligation:
            return False
        if obligation.paid_amount:
            raise ValueError("بدهی دارای پرداخت قابل حذف نیست")
        if obligation.journal_entry_id:
            raise ValueError(
                "بدهی ثبت‌شده در حسابداری قابل حذف نیست؛ از سند اصلاحی استفاده کنید"
            )
        obligation.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def get_total_obligations(db: Session, customer_id: int) -> int:
        total = db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == customer_id,
            FinancialObligation.is_deleted.is_(False),
            FinancialObligation.status != ObligationStatus.CANCELLED,
        ).with_entities(FinancialObligation.amount).all()
        return sum(row[0] for row in total) if total else 0
