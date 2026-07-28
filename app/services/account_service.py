from sqlalchemy.orm import Session
from app.models.account import Account, AccountType

class AccountService:
    @staticmethod
    def create(db: Session, data: dict) -> Account:
        account = Account(**data)
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def get_by_id(db: Session, account_id: int) -> Account | None:
        return db.query(Account).filter(
            Account.id == account_id,
            Account.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Account).filter(
            Account.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_type(db: Session, account_type: AccountType):
        return db.query(Account).filter(
            Account.account_type == account_type,
            Account.is_deleted == False
        ).all()

    @staticmethod
    def update(db: Session, account_id: int, data: dict) -> Account | None:
        account = AccountService.get_by_id(db, account_id)
        if not account:
            return None
        for key, value in data.items():
            setattr(account, key, value)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db: Session, account_id: int) -> bool:
        account = AccountService.get_by_id(db, account_id)
        if not account:
            return False
        account.is_deleted = True
        db.commit()
        return True