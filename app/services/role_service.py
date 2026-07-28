from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.permission import Permission

class RoleService:
    @staticmethod
    def create(db: Session, name: str, description: str = None, permissions: list = None) -> Role:
        role = Role(
            name=name,
            description=description,
            permissions=','.join(permissions) if permissions else ''
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_by_id(db: Session, role_id: int) -> Role | None:
        return db.query(Role).filter(
            Role.id == role_id,
            Role.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Role).filter(
            Role.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_permissions(db: Session, role_id: int, permissions: list) -> Role | None:
        role = RoleService.get_by_id(db, role_id)
        if not role:
            return None
        role.permissions = ','.join(permissions)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete(db: Session, role_id: int) -> bool:
        role = RoleService.get_by_id(db, role_id)
        if not role:
            return False
        role.is_deleted = True
        db.commit()
        return True