from datetime import date
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import (
    BankAccount, BankStatement, Customer, FinancialObligation, ObligationStatus,
    Payment, Project, ProjectMember, Receipt,
)
from app.services.ledger_service import LedgerService


class ReportService:
    @staticmethod
    def get_customer_statement(db: Session, customer_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, Any]:
        customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()
        if not customer:
            return {"error": "مشتری پیدا نشد"}
        transactions = LedgerService.get_entries(db, customer_id=customer_id, from_date=from_date, to_date=to_date)
        return {"customer": customer, "transactions": transactions, **LedgerService.summarize(transactions)}

    @staticmethod
    def get_project_financial_summary(db: Session, project_id: int) -> Dict[str, Any]:
        project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
        if not project:
            return {"error": "پروژه پیدا نشد"}
        members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.is_deleted == False).all()
        entries = LedgerService.get_entries(db, project_id=project_id)
        by_customer: dict[int, list[dict[str, Any]]] = {}
        for entry in entries:
            by_customer.setdefault(entry["customer_id"], []).append(entry)
        member_summaries = []
        for member in members:
            summary = LedgerService.summarize(by_customer.get(member.customer_id, []))
            member_summaries.append({"customer_no": member.customer.customer_no, "full_name": member.customer.full_name, **summary})
        overdue = db.query(FinancialObligation).filter(
            FinancialObligation.project_id == project_id,
            FinancialObligation.due_date < date.today(),
            FinancialObligation.status != ObligationStatus.PAID,
            FinancialObligation.status != ObligationStatus.CANCELLED,
            FinancialObligation.is_deleted == False,
        ).all()
        return {
            "project": project,
            "member_count": len(members),
            "member_summaries": member_summaries,
            "total_overdue": sum(obligation.amount - (obligation.paid_amount or 0) for obligation in overdue),
            **LedgerService.summarize(entries),
        }


    @staticmethod
    def get_management_dashboard(db: Session) -> Dict[str, Any]:
        from app.models.receipt import PaymentMethod, ReceiptStatus
        from app.models.project import Project
        from app.models.receipt import Receipt
        from sqlalchemy import func
        entries = LedgerService.get_entries(db)
        summary = LedgerService.summarize(entries)
        monthly = db.query(func.strftime("%Y-%m", Receipt.receipt_date), func.sum(Receipt.amount)).filter(Receipt.is_deleted == False, Receipt.status == ReceiptStatus.CONFIRMED).group_by(func.strftime("%Y-%m", Receipt.receipt_date)).order_by(func.strftime("%Y-%m", Receipt.receipt_date)).all()
        overdue_cheques = db.query(Receipt).filter(Receipt.payment_method == PaymentMethod.CHEQUE, Receipt.cheque_status == "PENDING_COLLECTION", Receipt.cheque_due_date < date.today(), Receipt.is_deleted == False).all()
        project_deficits = []
        for project in db.query(Project).filter(Project.is_deleted == False).all():
            value = LedgerService.summarize(LedgerService.get_entries(db, project_id=project.id))["net_balance"]
            if value > 0: project_deficits.append({"project": project, "balance": value})
        return {**summary, "monthly_receipts": [{"month": row[0], "amount": row[1] or 0} for row in monthly], "overdue_cheques": overdue_cheques, "project_deficits": project_deficits}

    @staticmethod
    def get_bank_report(
        db: Session,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """گزارش حساب بانکی"""
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        if not account:
            return {"error": "حساب بانکی پیدا نشد"}

        deposits = db.query(Receipt).filter(
            Receipt.bank_account_id == account_id,
            Receipt.is_deleted == False
        )
        if from_date:
            deposits = deposits.filter(Receipt.receipt_date >= from_date)
        if to_date:
            deposits = deposits.filter(Receipt.receipt_date <= to_date)
        deposits = deposits.all()

        withdrawals = db.query(Payment).filter(
            Payment.bank_account_id == account_id,
            Payment.is_deleted == False
        )
        if from_date:
            withdrawals = withdrawals.filter(Payment.payment_date >= from_date)
        if to_date:
            withdrawals = withdrawals.filter(Payment.payment_date <= to_date)
        withdrawals = withdrawals.all()

        transactions = []
        for d in deposits:
            transactions.append({
                "date": d.receipt_date,
                "description": d.description or "واریز",
                "type": "DEPOSIT",
                "amount": d.amount
            })
        for w in withdrawals:
            transactions.append({
                "date": w.payment_date,
                "description": w.description or "برداشت",
                "type": "WITHDRAWAL",
                "amount": w.amount
            })

        transactions.sort(key=lambda x: x["date"])

        balance = 0
        for t in transactions:
            if t["type"] == "DEPOSIT":
                balance += t["amount"]
            else:
                balance -= t["amount"]
            t["balance"] = balance

        total_deposits = sum([t["amount"] for t in transactions if t["type"] == "DEPOSIT"])
        total_withdrawals = sum([t["amount"] for t in transactions if t["type"] == "WITHDRAWAL"])

        return {
            "account": account,
            "transactions": transactions,
            "balance": balance,
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "transaction_count": len(transactions)
        }

    @staticmethod
    def get_bank_reconciliation(db: Session, account_id: int, statement_date: Optional[date] = None) -> Dict[str, Any]:
        """Compare confirmed system operations with imported bank rows by amount, type and reference/date."""
        account = db.query(BankAccount).filter(BankAccount.id == account_id, BankAccount.is_deleted == False).first()
        if not account:
            return {"error": "حساب بانکی پیدا نشد"}
        statements_query = db.query(BankStatement).filter(BankStatement.bank_account_id == account_id, BankStatement.is_deleted == False)
        if statement_date:
            statements_query = statements_query.filter(BankStatement.statement_date == statement_date)
        statements = statements_query.order_by(BankStatement.statement_date, BankStatement.id).all()
        system_items = [
            {"id": receipt.id, "date": receipt.receipt_date, "amount": receipt.amount, "type": "DEPOSIT", "reference": receipt.receipt_no, "description": receipt.description or "واریز ثبت شده"}
            for receipt in db.query(Receipt).filter(Receipt.bank_account_id == account_id, Receipt.is_deleted == False, Receipt.status == "CONFIRMED").all()
        ] + [
            {"id": payment.id, "date": payment.payment_date, "amount": payment.amount, "type": "WITHDRAWAL", "reference": payment.payment_no, "description": payment.description or "برداشت ثبت شده"}
            for payment in db.query(Payment).filter(Payment.bank_account_id == account_id, Payment.is_deleted == False, Payment.status == "CONFIRMED").all()
        ]
        unmatched_system = list(system_items); matched = []; unmatched_bank = []
        for statement in statements:
            statement_type = statement.statement_type.value if hasattr(statement.statement_type, "value") else statement.statement_type
            match = next((item for item in unmatched_system if item["amount"] == statement.amount and item["type"] == statement_type and (not statement.reference_no or statement.reference_no == item["reference"] or item["date"] == statement.statement_date)), None)
            if match:
                unmatched_system.remove(match); matched.append({"statement_id": statement.id, "system": match})
            else:
                unmatched_bank.append({"date": statement.statement_date, "description": statement.description or "تراکنش بانکی", "amount": statement.amount, "type": statement_type, "status": "فقط در بانک"})
        system_balance = sum(item["amount"] if item["type"] == "DEPOSIT" else -item["amount"] for item in system_items)
        bank_balance = statements[-1].balance if statements and statements[-1].balance is not None else 0
        return {"account": account, "system_balance": system_balance, "bank_balance": bank_balance, "difference": system_balance - bank_balance, "matched": matched, "unrecorded": [{**item, "status": "فقط در سیستم"} for item in unmatched_system] + unmatched_bank, "statement_count": len(statements)}
