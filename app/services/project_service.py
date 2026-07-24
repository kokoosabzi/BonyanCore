from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    @staticmethod
    def create(db: Session, data: ProjectCreate) -> Project:
        project = Project(**data.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Project | None:
        return db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()

    @staticmethod
    def get_by_code(db: Session, project_code: str) -> Project | None:
        return db.query(Project).filter(Project.project_code == project_code, Project.is_deleted == False).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, search: str = None):
        query = db.query(Project).filter(Project.is_deleted == False)
        if search:
            query = query.filter(
                or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.project_code.ilike(f"%{search}%")
                )
            )
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, project_id: int, data: ProjectUpdate) -> Project | None:
        project = ProjectService.get_by_id(db, project_id)
        if not project:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete(db: Session, project_id: int) -> bool:
        project = ProjectService.get_by_id(db, project_id)
        if not project:
            return False
        project.is_deleted = True
        db.commit()
        return True