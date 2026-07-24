from sqlalchemy.orm import Session
from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitUpdate

class UnitService:
    @staticmethod
    def create(db: Session, data: UnitCreate) -> Unit:
        unit = Unit(**data.model_dump())
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def get_by_id(db: Session, unit_id: int) -> Unit | None:
        return db.query(Unit).filter(
            Unit.id == unit_id,
            Unit.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, unit_code: str) -> Unit | None:
        return db.query(Unit).filter(
            Unit.unit_code == unit_code,
            Unit.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, project_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(Unit).filter(Unit.is_deleted == False)
        if project_id:
            query = query.filter(Unit.project_id == project_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, unit_id: int, data: UnitUpdate) -> Unit | None:
        unit = UnitService.get_by_id(db, unit_id)
        if not unit:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(unit, key, value)
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def delete(db: Session, unit_id: int) -> bool:
        unit = UnitService.get_by_id(db, unit_id)
        if not unit:
            return False
        unit.is_deleted = True
        db.commit()
        return True