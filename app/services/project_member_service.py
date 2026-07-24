from sqlalchemy.orm import Session
from app.models.project_member import ProjectMember
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberUpdate

class ProjectMemberService:
    @staticmethod
    def create(db: Session, data: ProjectMemberCreate) -> ProjectMember:
        existing = db.query(ProjectMember).filter(
            ProjectMember.customer_id == data.customer_id,
            ProjectMember.project_id == data.project_id,
            ProjectMember.is_deleted == False
        ).first()
        if existing:
            raise ValueError("این مشتری قبلاً در این پروژه عضو شده است")
        member = ProjectMember(**data.model_dump())
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def get_by_id(db: Session, member_id: int) -> ProjectMember | None:
        return db.query(ProjectMember).filter(
            ProjectMember.id == member_id,
            ProjectMember.is_deleted == False
        ).first()

    @staticmethod
    def get_by_customer_project(db: Session, customer_id: int, project_id: int) -> ProjectMember | None:
        return db.query(ProjectMember).filter(
            ProjectMember.customer_id == customer_id,
            ProjectMember.project_id == project_id,
            ProjectMember.is_deleted == False
        ).first()

    @staticmethod
    def get_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
        return db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_customer(db: Session, customer_id: int):
        return db.query(ProjectMember).filter(
            ProjectMember.customer_id == customer_id,
            ProjectMember.is_deleted == False
        ).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(ProjectMember).filter(
            ProjectMember.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, member_id: int, data: ProjectMemberUpdate) -> ProjectMember | None:
        member = ProjectMemberService.get_by_id(db, member_id)
        if not member:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(member, key, value)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def delete(db: Session, member_id: int) -> bool:
        member = ProjectMemberService.get_by_id(db, member_id)
        if not member:
            return False
        member.is_deleted = True
        db.commit()
        return True