from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, timedelta
from typing import Dict, List, Any, Optional
from app.models import (
    Customer, Project, ProjectMember, Contract,
    FinancialObligation, FinancialCredit,
    Receipt, Payment, BankAccount, BankStatement,
    JournalEntry, JournalLine
)
from app.services.financial_obligation_service import FinancialObligationService
from app.services.financial_credit_service import FinancialCreditService

class ReportService:
    @staticmethod
    def get_customer_statement(
        db: Session,
        customer_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """صورت حساب مشتری"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "مشتری پیدا نشد"}

        # بدهی‌ها
        obligations = db.query(FinancialObligation).filter(
            FinancialObligation.customer_id == customer_id,
            FinancialObligation.is_deleted == False
        )
        if from_date:
            obligations = obligations.filter(FinancialObligation.created_at >= from_date)
        if to_date:
            obligations = obligations.filter(FinancialObligation.created_at <= to_date)
        obligations = obligations.all()

        # اعتبارات
        credits = db.query(FinancialCredit).filter(
            FinancialCredit.customer_id == customer_id,
            FinancialCredit.is_deleted == False
        )
        if from_date:
            credits = credits.filter(FinancialCredit.created_at >= from_date)
        if to_date:
            credits = credits.filter(FinancialCredit.created_at <= to_date)
        credits = credits.all()

        # محاسبه مجموع
        total_obligations = sum([o.amount - o.paid_amount for o in obligations])
        total_credits = sum([c.amount for c in credits])

        # ایجاد لیست تراکنش‌ها
        transactions = []
        for o in obligations:
            transactions.append({
                "date": o.created_at,
                "type": "OBLIGATION",
                "description": o.description or "بدهی",
                "debit": o.amount - o.paid_amount,
                "credit": 0,
                "balance": 0
            })
        for c in credits:
            transactions.append({
                "date": c.created_at,
                "type": "CREDIT",
                "description": c.description or "اعتبار",
                "debit": 0,
                "credit": c.amount,
                "balance": 0
            })

        # مرتب‌سازی بر اساس تاریخ
        transactions.sort(key=lambda x: x["date"])

        # محاسبه مانده
        running_balance = 0
        for t in transactions:
            running_balance += t["debit"] - t["credit"]
            t["balance"] = running_balance

        return {
            "customer": customer,
            "transactions": transactions,
            "total_obligations": total_obligations,
            "total_credits": total_credits,
            "net_balance": total_obligations - total_credits,
            "total_debit": sum([t["debit"] for t in transactions]),
            "total_credit": sum([t["credit"] for t in transactions])
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
    def get_bank_reconciliation(
        db: Session,
        account_id: int,
        statement_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """گزارش مغایرت بانکی"""
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        if not account:
            return {"error": "حساب بانکی پیدا نشد"}

        statements = db.query(BankStatement).filter(
            BankStatement.bank_account_id == account_id,
            BankStatement.is_deleted == False
        )
        if statement_date:
            statements = statements.filter(BankStatement.statement_date == statement_date)
        statements = statements.all()

        receipts = db.query(Receipt).filter(
            Receipt.bank_account_id == account_id,
            Receipt.is_deleted == False,
            Receipt.status == "CONFIRMED"
        ).all()

        payments = db.query(Payment).filter(
            Payment.bank_account_id == account_id,
            Payment.is_deleted == False,
            Payment.status == "CONFIRMED"
        ).all()

        system_balance = 0
        for r in receipts:
            system_balance += r.amount
        for p in payments:
            system_balance -= p.amount

        bank_balance = 0
        if statements:
            bank_balance = statements[-1].balance if statements else 0

        unrecorded = []
        for r in receipts:
            if r.bank_account_id == account_id:
                unrecorded.append({
                    "date": r.receipt_date,
                    "description": r.description or "واریز ثبت شده",
                    "amount": r.amount,
                    "type": "DEPOSIT",
                    "status": "در سیستم ثبت شده"
                })

        return {
            "account": account,
            "system_balance": system_balance,
            "bank_balance": bank_balance,
            "difference": system_balance - bank_balance,
            "unrecorded": unrecorded,
            "statement_count": len(statements)
        }