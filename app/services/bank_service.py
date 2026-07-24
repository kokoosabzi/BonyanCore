from sqlalchemy.orm import Session
from app.models.bank import Bank
from app.schemas.bank import BankCreate, BankUpdate

class BankService:
    @staticmethod
    def create(db: Session, data: BankCreate) -> Bank:
        bank = Bank(**data.model_dump())
        db.add(bank)
        db.commit()
        db.refresh(bank)
        return bank

    @staticmethod
    def get_by_id(db: Session, bank_id: int) -> Bank | None:
        return db.query(Bank).filter(
            Bank.id == bank_id,
            Bank.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Bank).filter(
            Bank.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, bank_id: int, data: BankUpdate) -> Bank | None:
        bank = BankService.get_by_id(db, bank_id)
        if not bank:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(bank, key, value)
        db.commit()
        db.refresh(bank)
        return bank

    @staticmethod
    def delete(db: Session, bank_id: int) -> bool:
        bank = BankService.get_by_id(db, bank_id)
        if not bank:
            return False
        bank.is_deleted = True
        db.commit()
        return True