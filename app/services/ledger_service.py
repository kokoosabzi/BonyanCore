"""Read-only financial ledger assembled from the system's operational records."""
from datetime import date
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.financial_credit import CreditStatus, FinancialCredit
from app.models.financial_obligation import FinancialObligation, ObligationStatus
from app.models.receipt import Receipt, ReceiptStatus


class LedgerService:
    """Provide one consistent member/project financial view without a new table.

    The ledger deliberately includes only financially effective records: active
    obligations, non-reversed credits, and confirmed receipts. Journal entries
    are not added as separate rows because receipt journals represent the same
    business event and would otherwise be counted twice.
    """

    @staticmethod
    def get_entries(
        db: Session,
        *,
        customer_id: Optional[int] = None,
        project_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []

        obligations = db.query(FinancialObligation).filter(
            FinancialObligation.is_deleted == False,
            FinancialObligation.status != ObligationStatus.CANCELLED,
        )
        credits = db.query(FinancialCredit).filter(
            FinancialCredit.is_deleted == False,
            FinancialCredit.status != CreditStatus.REVERSED,
        )
        receipts = db.query(Receipt).filter(
            Receipt.is_deleted == False,
            Receipt.status == ReceiptStatus.CONFIRMED,
            (Receipt.cheque_status.is_(None)) | (Receipt.cheque_status == "COLLECTED"),
        )
        for query, model in ((obligations, FinancialObligation), (credits, FinancialCredit), (receipts, Receipt)):
            if customer_id is not None:
                query = query.filter(model.customer_id == customer_id)
            if project_id is not None:
                query = query.filter(model.project_id == project_id)
            if model is FinancialCredit:
                if from_date:
                    query = query.filter(model.credit_date >= from_date)
                if to_date:
                    query = query.filter(model.credit_date <= to_date)
            elif model is Receipt:
                if from_date:
                    query = query.filter(model.receipt_date >= from_date)
                if to_date:
                    query = query.filter(model.receipt_date <= to_date)
            else:
                # Obligations have no business-date field; use their creation date.
                if from_date:
                    query = query.filter(model.created_at >= from_date)
                if to_date:
                    query = query.filter(model.created_at < date.fromordinal(to_date.toordinal() + 1))

            for record in query.all():
                if model is FinancialObligation:
                    entries.append(LedgerService._entry(
                        record.created_at.date(), record.customer_id, record.project_id,
                        "OBLIGATION", record.id, record.obligation_no,
                        record.description or "بدهی", debit=record.amount - (record.paid_amount or 0),
                    ))
                elif model is FinancialCredit:
                    entries.append(LedgerService._entry(
                        record.credit_date, record.customer_id, record.project_id,
                        "CREDIT", record.id, record.credit_no,
                        record.description or "اعتبار", credit=record.amount,
                    ))
                else:
                    entries.append(LedgerService._entry(
                        record.receipt_date, record.customer_id, record.project_id,
                        "RECEIPT", record.id, record.receipt_no,
                        record.description or "دریافت عضو", credit=record.amount,
                    ))

        entries.sort(key=lambda entry: (entry["date"], entry["source_type"], entry["source_id"]))
        balance = 0
        for entry in entries:
            balance += entry["debit"] - entry["credit"]
            entry["balance"] = balance
        return entries

    @staticmethod
    def summarize(entries: list[dict[str, Any]]) -> dict[str, int]:
        total_debit = sum(entry["debit"] for entry in entries)
        total_credit = sum(entry["credit"] for entry in entries)
        total_receipts = sum(entry["credit"] for entry in entries if entry["source_type"] == "RECEIPT")
        total_credits = sum(entry["credit"] for entry in entries if entry["source_type"] == "CREDIT")
        return {
            "total_obligations": total_debit,
            "total_credits": total_credits,
            "total_receipts": total_receipts,
            "total_received": total_credit,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "net_balance": total_debit - total_credit,
        }

    @staticmethod
    def _entry(
        entry_date: date, customer_id: int, project_id: int, source_type: str,
        source_id: int, reference_no: str, description: str, *, debit: int = 0, credit: int = 0,
    ) -> dict[str, Any]:
        return {
            "date": entry_date,
            "customer_id": customer_id,
            "project_id": project_id,
            "source_type": source_type,
            "source_id": source_id,
            "reference_no": reference_no,
            "description": description,
            "debit": debit,
            "credit": credit,
            "balance": 0,
        }
