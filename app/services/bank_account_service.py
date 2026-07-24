from sqlalchemy.orm import Session
from app.models.bank_account import BankAccount
from app.schemas.bank_account import BankAccountCreate, BankAccountUpdate

class BankAccountService:
    @staticmethod
    def create(db: Session, data: BankAccountCreate) -> BankAccount:
        account = BankAccount(**data.model_dump())
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def get_by_id(db: Session, account_id: int) -> BankAccount | None:
        return db.query(BankAccount).filter(
            BankAccount.id == account_id,
            BankAccount.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(BankAccount).filter(
            BankAccount.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_bank(db: Session, bank_id: int):
        return db.query(BankAccount).filter(
            BankAccount.bank_id == bank_id,
            BankAccount.is_deleted == False
        ).all()

    @staticmethod
    def update(db: Session, account_id: int, data: BankAccountUpdate) -> BankAccount | None:
        account = BankAccountService.get_by_id(db, account_id)
        if not account:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(account, key, value)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db: Session, account_id: int) -> bool:
        account = BankAccountService.get_by_id(db, account_id)
        if not account:
            return False
        account.is_deleted = True
        db.commit()
        return True