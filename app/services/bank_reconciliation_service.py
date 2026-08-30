from datetime import date
from sqlalchemy.orm import Session
from app.models.bank_reconciliation_match import BankReconciliationMatch
from app.models.bank_statement import BankStatement

class BankReconciliationService:
    @staticmethod
    def save_match(db: Session, statement_id: int, source_type: str, source_id: int, confirmed: bool = False):
        statement = db.query(BankStatement).filter(BankStatement.id == statement_id, BankStatement.is_deleted == False).first()
        if not statement: return None
        match = db.query(BankReconciliationMatch).filter(BankReconciliationMatch.bank_statement_id == statement_id).first()
        if not match:
            match = BankReconciliationMatch(bank_statement_id=statement_id, source_type=source_type, source_id=source_id, matched_at=date.today(), is_confirmed=confirmed); db.add(match)
        else:
            match.source_type=source_type; match.source_id=source_id; match.is_confirmed=confirmed; match.matched_at=date.today()
        statement.is_reconciled = confirmed
        db.commit(); db.refresh(match); return match
    @staticmethod
    def confirm(db: Session, statement_id: int):
        match=db.query(BankReconciliationMatch).filter(BankReconciliationMatch.bank_statement_id==statement_id).first()
        if not match: return None
        match.is_confirmed=True; statement=db.query(BankStatement).filter(BankStatement.id==statement_id).first(); statement.is_reconciled=True; db.commit(); db.refresh(match); return match
