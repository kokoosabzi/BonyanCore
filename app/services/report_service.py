from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from app.models import (
    Customer, Project, ProjectMember, Contract,
    FinancialObligation, FinancialCredit,
    Receipt, Payment, BankAccount, BankStatement,
    JournalEntry, JournalLine
)
from app.services.financial_obligation_service import FinancialObligationService
from app.services.financial_credit_service import FinancialCreditService
from app.models.financial_obligation import ObligationStatus
from app.models.financial_credit import CreditStatus
from app.models.receipt import ReceiptStatus
from app.models.payment import PaymentStatus

class ReportService:
    @staticmethod
    def _validate_date_range(
        from_date: Optional[date], to_date: Optional[date]
    ) -> None:
        """Validate report boundaries before they are used in a financial query."""
        for value in (from_date, to_date):
            if value is not None and (not isinstance(value, date) or isinstance(value, datetime)):
                raise ValueError("تاریخ فیلتر گزارش معتبر نیست")
        if from_date and to_date and from_date > to_date:
            raise ValueError("تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد")

    @staticmethod
    def get_customer_statement(
        db: Session,
        customer_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Return a customer statement with opening balance and effective dates."""
        ReportService._validate_date_range(from_date, to_date)
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "مشتری پیدا نشد"}

        obligations = db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == customer_id,
            FinancialObligation.is_deleted.is_(False),
            FinancialObligation.status != ObligationStatus.CANCELLED,
        )
        credits = db.query(FinancialCredit).filter(
            FinancialCredit.customer_id == customer_id,
            FinancialCredit.is_deleted.is_(False),
            FinancialCredit.status == CreditStatus.APPROVED,
        )

        obligation_effective_date = func.coalesce(
            FinancialObligation.due_date,
            func.date(FinancialObligation.created_at),
        )
        opening_obligations = []
        opening_credits = []
        if from_date:
            opening_obligations = obligations.filter(
                obligation_effective_date < from_date
            ).all()
            opening_credits = credits.filter(
                FinancialCredit.credit_date < from_date
            ).all()
            obligations = obligations.filter(obligation_effective_date >= from_date)
            credits = credits.filter(FinancialCredit.credit_date >= from_date)
        if to_date:
            obligations = obligations.filter(obligation_effective_date <= to_date)
            credits = credits.filter(FinancialCredit.credit_date <= to_date)

        obligations = obligations.all()
        credits = credits.all()
        opening_debit = sum(o.amount for o in opening_obligations)
        opening_credit = sum(c.amount for c in opening_credits)
        opening_balance = opening_debit - opening_credit
        total_obligations = sum(o.amount for o in obligations)
        total_credits = sum(c.amount for c in credits)

        transactions = []
        for obligation in obligations:
            created_at = obligation.created_at
            effective_date = obligation.due_date or (
                created_at.date() if hasattr(created_at, "date") else created_at
            )
            transactions.append({
                "date": effective_date,
                "type": "OBLIGATION",
                "description": obligation.description or "بدهی",
                "debit": obligation.amount,
                "credit": 0,
                "balance": 0,
            })
        for credit in credits:
            transactions.append({
                "date": credit.credit_date,
                "type": "CREDIT",
                "description": credit.description or "اعتبار",
                "debit": 0,
                "credit": credit.amount,
                "balance": 0,
            })

        transactions.sort(key=lambda item: item["date"])
        running_balance = opening_balance
        for transaction in transactions:
            running_balance += transaction["debit"] - transaction["credit"]
            transaction["balance"] = running_balance

        return {
            "customer": customer,
            "transactions": transactions,
            "opening_debit": opening_debit,
            "opening_credit": opening_credit,
            "opening_balance": opening_balance,
            "total_obligations": total_obligations,
            "total_credits": total_credits,
            "period_balance": total_obligations - total_credits,
            "net_balance": running_balance,
            "total_debit": sum(item["debit"] for item in transactions),
            "total_credit": sum(item["credit"] for item in transactions),
        }

    @staticmethod
    def get_project_financial_summary(
        db: Session,
        project_id: int
    ) -> Dict[str, Any]:
        """خلاصه مالی پروژه"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "پروژه پیدا نشد"}

        members = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.is_deleted == False
        ).all()

        member_summaries = []
        total_obligations = 0
        total_credits = 0

        for member in members:
            customer = member.customer
            obligations = db.query(FinancialObligation).filter(
                FinancialObligation.customer_id == customer.id,
                FinancialObligation.project_id == project_id,
                FinancialObligation.is_deleted == False
            ).all()
            credits = db.query(FinancialCredit).filter(
                FinancialCredit.customer_id == customer.id,
                FinancialCredit.project_id == project_id,
                FinancialCredit.is_deleted == False
            ).all()

            total_obligation = sum([o.amount - o.paid_amount for o in obligations])
            total_credit = sum([c.amount for c in credits])
            balance = total_obligation - total_credit

            total_obligations += total_obligation
            total_credits += total_credit

            member_summaries.append({
                "customer_no": customer.customer_no,
                "full_name": customer.full_name,
                "total_obligations": total_obligation,
                "total_credits": total_credit,
                "balance": balance
            })

        overdue = db.query(FinancialObligation).filter(
            FinancialObligation.project_id == project_id,
            FinancialObligation.due_date < date.today(),
            FinancialObligation.status != "PAID",
            FinancialObligation.is_deleted == False
        ).all()
        total_overdue = sum([o.amount - o.paid_amount for o in overdue])

        return {
            "project": project,
            "member_count": len(members),
            "member_summaries": member_summaries,
            "total_obligations": total_obligations,
            "total_credits": total_credits,
            "total_overdue": total_overdue
        }

    @staticmethod
    def get_bank_report(
        db: Session,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Report confirmed bank movements only, in a stable date/id order."""
        ReportService._validate_date_range(from_date, to_date)
        account = db.query(BankAccount).filter(
            BankAccount.id == account_id,
            BankAccount.is_deleted.is_(False),
        ).first()
        if not account:
            return {"error": "حساب بانکی پیدا نشد"}

        deposits_query = db.query(Receipt).filter(
            Receipt.bank_account_id == account_id,
            Receipt.is_deleted.is_(False),
            Receipt.status == ReceiptStatus.CONFIRMED,
        )
        withdrawals_query = db.query(Payment).filter(
            Payment.bank_account_id == account_id,
            Payment.is_deleted.is_(False),
            Payment.status == PaymentStatus.CONFIRMED,
        )
        if from_date:
            deposits_query = deposits_query.filter(Receipt.receipt_date >= from_date)
            withdrawals_query = withdrawals_query.filter(Payment.payment_date >= from_date)
        if to_date:
            deposits_query = deposits_query.filter(Receipt.receipt_date <= to_date)
            withdrawals_query = withdrawals_query.filter(Payment.payment_date <= to_date)

        deposits = deposits_query.order_by(Receipt.receipt_date.asc(), Receipt.id.asc()).all()
        withdrawals = withdrawals_query.order_by(Payment.payment_date.asc(), Payment.id.asc()).all()
        transactions = []
        for receipt in deposits:
            transactions.append({
                "date": receipt.receipt_date,
                "description": receipt.description or "واریز",
                "type": "DEPOSIT",
                "amount": receipt.amount,
                "source_id": receipt.id,
            })
        for payment in withdrawals:
            transactions.append({
                "date": payment.payment_date,
                "description": payment.description or "برداشت",
                "type": "WITHDRAWAL",
                "amount": payment.amount,
                "source_id": payment.id,
            })

        transactions.sort(key=lambda item: (item["date"], item["source_id"]))
        balance = 0
        for transaction in transactions:
            balance += transaction["amount"] if transaction["type"] == "DEPOSIT" else -transaction["amount"]
            transaction["balance"] = balance

        total_deposits = sum(item["amount"] for item in transactions if item["type"] == "DEPOSIT")
        total_withdrawals = sum(item["amount"] for item in transactions if item["type"] == "WITHDRAWAL")
        return {
            "account": account,
            "transactions": transactions,
            "balance": balance,
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "transaction_count": len(transactions),
        }

    @staticmethod
    def reconcile_bank_statement(
        db: Session,
        statement_id: int,
        receipt_id: Optional[int] = None,
        payment_id: Optional[int] = None,
    ) -> BankStatement:
        """ثبت تطبیق دستی و قطعی یک رکورد بانکی با سند سیستم."""
        if (receipt_id is None) == (payment_id is None):
            raise ValueError("دقیقاً یکی از receipt_id یا payment_id باید مشخص شود")

        statement = db.query(BankStatement).filter(
            BankStatement.id == statement_id,
            BankStatement.is_deleted.is_(False),
        ).first()
        if not statement:
            raise ValueError("رکورد صورت‌حساب بانکی پیدا نشد")
        if statement.is_reconciled:
            raise ValueError("این رکورد بانکی قبلاً تطبیق داده شده است")

        if receipt_id is not None:
            receipt = db.query(Receipt).filter(
                Receipt.id == receipt_id,
                Receipt.is_deleted.is_(False),
                Receipt.status == "CONFIRMED",
            ).first()
            if not receipt:
                raise ValueError("دریافت تأییدشده پیدا نشد")
            if receipt.bank_account_id != statement.bank_account_id:
                raise ValueError("حساب بانکی دریافت با صورت‌حساب یکسان نیست")
            if receipt.amount != statement.amount or receipt.receipt_date != statement.statement_date:
                raise ValueError("مبلغ و تاریخ دریافت با رکورد بانکی یکسان نیست")
            if statement.statement_type.value != "DEPOSIT":
                raise ValueError("رکورد بانکی برداشت است و با دریافت قابل تطبیق نیست")
            if db.query(BankStatement).filter(
                BankStatement.receipt_id == receipt.id,
                BankStatement.is_deleted.is_(False),
            ).first():
                raise ValueError("این دریافت قبلاً با یک رکورد بانکی تطبیق داده شده است")
            statement.receipt_id = receipt.id
            statement.payment_id = None
        else:
            payment = db.query(Payment).filter(
                Payment.id == payment_id,
                Payment.is_deleted.is_(False),
                Payment.status == "CONFIRMED",
            ).first()
            if not payment:
                raise ValueError("پرداخت تأییدشده پیدا نشد")
            if payment.bank_account_id != statement.bank_account_id:
                raise ValueError("حساب بانکی پرداخت با صورت‌حساب یکسان نیست")
            if payment.amount != statement.amount or payment.payment_date != statement.statement_date:
                raise ValueError("مبلغ و تاریخ پرداخت با رکورد بانکی یکسان نیست")
            if statement.statement_type.value != "WITHDRAWAL":
                raise ValueError("رکورد بانکی واریز است و با پرداخت قابل تطبیق نیست")
            if db.query(BankStatement).filter(
                BankStatement.payment_id == payment.id,
                BankStatement.is_deleted.is_(False),
            ).first():
                raise ValueError("این پرداخت قبلاً با یک رکورد بانکی تطبیق داده شده است")
            statement.payment_id = payment.id
            statement.receipt_id = None

        statement.is_reconciled = True
        db.commit()
        db.refresh(statement)
        return statement

    @staticmethod
    def unreconcile_bank_statement(db: Session, statement_id: int) -> BankStatement:
        """لغو تطبیق دستی رکورد صورت‌حساب."""
        statement = db.query(BankStatement).filter(
            BankStatement.id == statement_id,
            BankStatement.is_deleted.is_(False),
        ).first()
        if not statement:
            raise ValueError("رکورد صورت‌حساب بانکی پیدا نشد")
        statement.receipt_id = None
        statement.payment_id = None
        statement.is_reconciled = False
        db.commit()
        db.refresh(statement)
        return statement

    @staticmethod
    def get_bank_reconciliation(
        db: Session,
        account_id: int,
        statement_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """گزارش کامل مغایرت بانکی بر اساس تطبیق تراکنش‌های بانک و سیستم."""
        account = db.query(BankAccount).filter(
            BankAccount.id == account_id,
            BankAccount.is_deleted.is_(False),
        ).first()
        if not account:
            return {"error": "حساب بانکی پیدا نشد"}

        # اگر تاریخ مشخص شده باشد، مانده بانک در همان تاریخ/آخرین رکورد قبل از آن
        # مبنای گزارش است. در غیر این صورت آخرین صورت‌حساب ثبت‌شده مبناست.
        statement_query = db.query(BankStatement).filter(
            BankStatement.bank_account_id == account_id,
            BankStatement.is_deleted.is_(False),
        )
        if statement_date:
            statement_query = statement_query.filter(
                BankStatement.statement_date <= statement_date
            )

        statements = statement_query.order_by(
            BankStatement.statement_date.asc(),
            BankStatement.id.asc(),
        ).all()

        if not statements:
            return {
                "error": "برای این حساب صورت‌حساب بانکی ثبت نشده است",
                "account": account,
                "system_balance": 0,
                "bank_balance": 0,
                "difference": 0,
                "unrecorded": [],
                "system_only": [],
                "matched": [],
                "statement_count": 0,
            }

        effective_date = statement_date or statements[-1].statement_date
        latest_statement = statements[-1]

        # فقط تراکنش‌های تأییدشده تا تاریخ صورت‌حساب وارد محاسبه سیستم می‌شوند.
        receipts = db.query(Receipt).filter(
            Receipt.bank_account_id == account_id,
            Receipt.is_deleted.is_(False),
            Receipt.status == "CONFIRMED",
            Receipt.receipt_date <= effective_date,
        ).order_by(Receipt.receipt_date.asc(), Receipt.id.asc()).all()

        payments = db.query(Payment).filter(
            Payment.bank_account_id == account_id,
            Payment.is_deleted.is_(False),
            Payment.status == "CONFIRMED",
            Payment.payment_date <= effective_date,
        ).order_by(Payment.payment_date.asc(), Payment.id.asc()).all()

        # تراکنش‌های بانکی تا تاریخ مبنا.
        bank_transactions = [
            {
                "id": s.id,
                "date": s.statement_date,
                "description": s.description or (
                    "واریز بانکی" if s.statement_type.value == "DEPOSIT" else "برداشت بانکی"
                ),
                "amount": s.amount,
                "type": s.statement_type.value,
                "reference_no": s.reference_no,
                "balance": s.balance,
            }
            for s in statements
        ]

        # تطبیق قطعی/نزدیک: نوع + مبلغ + تاریخ؛ در صورت وجود شماره مرجع،
        # شماره مرجع نیز برای اولویت‌بندی استفاده می‌شود. هر رکورد بانک فقط
        # یک بار می‌تواند با یک رکورد سیستم تطبیق داده شود.
        system_transactions = []
        for r in receipts:
            system_transactions.append({
                "id": r.id,
                "date": r.receipt_date,
                "description": r.description or f"دریافت {r.receipt_no}",
                "amount": r.amount,
                "type": "DEPOSIT",
                "reference_no": r.reference_no,
                "document_no": r.receipt_no,
            })
        for p in payments:
            system_transactions.append({
                "id": p.id,
                "date": p.payment_date,
                "description": p.description or f"پرداخت {p.payment_no}",
                "amount": p.amount,
                "type": "WITHDRAWAL",
                "reference_no": None,
                "document_no": p.payment_no,
            })

        system_transactions.sort(key=lambda x: (x["date"], x["id"]))

        used_bank_ids = set()
        matched = []
        system_only = []

        # تطبیق‌های دستی و قطعی بر تطبیق خودکار اولویت دارند.
        system_by_key = {(tx["type"], tx["id"]): tx for tx in system_transactions}
        for bank_tx in bank_transactions:
            statement = next((s for s in statements if s.id == bank_tx["id"]), None)
            if not statement or not statement.is_reconciled:
                continue
            target_id = statement.receipt_id if statement.receipt_id is not None else statement.payment_id
            target_type = "DEPOSIT" if statement.receipt_id is not None else "WITHDRAWAL"
            system_tx = system_by_key.get((target_type, target_id))
            if not system_tx:
                continue
            used_bank_ids.add(bank_tx["id"])
            matched.append({
                "date": bank_tx["date"],
                "description": bank_tx["description"],
                "amount": bank_tx["amount"],
                "type": bank_tx["type"],
                "system_document_no": system_tx["document_no"],
                "bank_reference_no": bank_tx["reference_no"],
                "status": "تطبیق دستی",
                "manual": True,
                "bank_statement_id": bank_tx["id"],
                "system_id": target_id,
            })

        for system_tx in system_transactions:
            candidates = [
                bank_tx for bank_tx in bank_transactions
                if bank_tx["id"] not in used_bank_ids
                and not next((s.is_reconciled for s in statements if s.id == bank_tx["id"]), False)
                and bank_tx["date"] == system_tx["date"]
                and bank_tx["amount"] == system_tx["amount"]
                and bank_tx["type"] == system_tx["type"]
            ]

            if system_tx["reference_no"]:
                reference_matches = [
                    item for item in candidates
                    if item["reference_no"] == system_tx["reference_no"]
                ]
                if reference_matches:
                    candidates = reference_matches

            if candidates:
                bank_tx = candidates[0]
                used_bank_ids.add(bank_tx["id"])
                matched.append({
                    "date": system_tx["date"],
                    "description": system_tx["description"],
                    "amount": system_tx["amount"],
                    "type": system_tx["type"],
                    "system_document_no": system_tx["document_no"],
                    "bank_reference_no": bank_tx["reference_no"],
                    "status": "مطابقت دارد",
                    "manual": False,
                    "bank_statement_id": bank_tx["id"],
                    "system_id": system_tx["id"],
                })
            else:
                system_only.append({
                    **system_tx,
                    "status": "در سیستم ثبت شده ولی در بانک یافت نشد",
                })

        bank_only = []
        for bank_tx in bank_transactions:
            if bank_tx["id"] in used_bank_ids:
                continue
            candidates = [
                {
                    "id": tx["id"],
                    "document_no": tx["document_no"],
                    "type": tx["type"],
                }
                for tx in system_transactions
                if tx["date"] == bank_tx["date"]
                and tx["amount"] == bank_tx["amount"]
                and tx["type"] == bank_tx["type"]
            ]
            bank_only.append({
                **bank_tx,
                "status": "در بانک ثبت شده ولی در سیستم یافت نشد",
                "candidate_system_transactions": candidates,
            })

        # مانده صورت‌حساب بانک، مانده واقعی اعلام‌شده توسط بانک است.
        bank_balance = latest_statement.balance
        bank_balance_known = bank_balance is not None

        # برای مقایسه مانده سیستم و بانک، از اولین مانده شناخته‌شده بانک
        # به‌عنوان مانده افتتاحیه مبنا استفاده می‌کنیم. این کار مانده صفر
        # مصنوعی قبلی را حذف می‌کند و اختلاف را بر مبنای یک نقطه مشترک می‌سنجد.
        baseline_statement = next(
            (s for s in statements if s.balance is not None),
            None,
        )
        opening_balance = None
        system_balance = None

        if baseline_statement is not None:
            signed_baseline = (
                baseline_statement.amount
                if baseline_statement.statement_type.value == "DEPOSIT"
                else -baseline_statement.amount
            )
            opening_balance = baseline_statement.balance - signed_baseline

            system_net_after_baseline = 0
            for tx in system_transactions:
                if tx["date"] >= baseline_statement.statement_date:
                    system_net_after_baseline += (
                        tx["amount"]
                        if tx["type"] == "DEPOSIT"
                        else -tx["amount"]
                    )
            system_balance = opening_balance + system_net_after_baseline

        difference = (
            system_balance - bank_balance
            if system_balance is not None and bank_balance_known
            else None
        )

        return {
            "account": account,
            "statement_date": effective_date,
            "system_balance": system_balance,
            "bank_balance": bank_balance,
            "difference": difference,
            "opening_balance": opening_balance,
            "bank_balance_known": bank_balance_known,
            "unrecorded": bank_only,
            "bank_only": bank_only,
            "system_only": system_only,
            "matched": matched,
            "statement_count": len(statements),
            "bank_transaction_count": len(bank_transactions),
            "system_transaction_count": len(system_transactions),
            "matched_count": len(matched),
            "bank_only_count": len(bank_only),
            "system_only_count": len(system_only),
        }
