from sqlalchemy.orm import Session
from app.models.contract import Contract, ContractType
from app.schemas.contract import ContractCreate, ContractUpdate
from app.services.document_sequence_service import DocumentSequenceService

class ContractService:
    @staticmethod
    def create(db: Session, data: ContractCreate) -> Contract:
        contract_no = DocumentSequenceService.get_next_contract_number(db)
        contract = Contract(contract_no=contract_no, **data.model_dump())
        db.add(contract)
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def get_by_id(db: Session, contract_id: int) -> Contract | None:
        return db.query(Contract).filter(
            Contract.id == contract_id,
            Contract.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, project_member_id: int = None, contract_type: ContractType = None, skip: int = 0, limit: int = 100):
        query = db.query(Contract).filter(Contract.is_deleted == False)
        if project_member_id:
            query = query.filter(Contract.project_member_id == project_member_id)
        if contract_type:
            query = query.filter(Contract.contract_type == contract_type)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, contract_id: int, data: ContractUpdate) -> Contract | None:
        contract = ContractService.get_by_id(db, contract_id)
        if not contract:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(contract, key, value)
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def delete(db: Session, contract_id: int) -> bool:
        contract = ContractService.get_by_id(db, contract_id)
        if not contract:
            return False
        contract.is_deleted = True
        db.commit()
        return True