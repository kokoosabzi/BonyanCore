from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.contract import ContractCreate, ContractUpdate, ContractResponse, ContractType
from app.models.contract import Contract
from app.services.contract_service import ContractService
from app.services.project_member_service import ProjectMemberService

router = APIRouter(prefix="/api/v1/contracts", tags=["Contracts"])

@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(data: ContractCreate, db: Session = Depends(get_db)):
    member = ProjectMemberService.get_by_id(db, data.project_member_id)
    if not member:
        raise HTTPException(status_code=404, detail="عضویت پیدا نشد")
    existing = db.query(Contract).filter(
        Contract.project_member_id == data.project_member_id,
        Contract.contract_type == data.contract_type,
        Contract.is_deleted == False
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"قبلاً قرارداد {data.contract_type} برای این عضو ثبت شده است")
    return ContractService.create(db, data)

@router.get("/", response_model=List[ContractResponse])
def get_contracts(
    project_member_id: Optional[int] = Query(None),
    contract_type: Optional[ContractType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return ContractService.get_all(db, project_member_id, contract_type, skip, limit)

@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = ContractService.get_by_id(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="قرارداد پیدا نشد")
    return contract

@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(contract_id: int, data: ContractUpdate, db: Session = Depends(get_db)):
    contract = ContractService.update(db, contract_id, data)
    if not contract:
        raise HTTPException(status_code=404, detail="قرارداد پیدا نشد")
    return contract

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    if not ContractService.delete(db, contract_id):
        raise HTTPException(status_code=404, detail="قرارداد پیدا نشد")