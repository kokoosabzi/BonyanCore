import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.role import Role
from app.models.user import User
from app.utils.security import get_password_hash


logger = logging.getLogger("bonyancore.bootstrap")


class BootstrapService:
    @staticmethod
    def ensure_default_admin(db: Session) -> User:
        user = db.query(User).filter(
            User.username == settings.DEFAULT_ADMIN_USERNAME
        ).first()
        if user:
            changed = False
            if user.is_deleted:
                user.is_deleted = False
                user.deleted_at = None
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if changed:
                db.commit()
                db.refresh(user)
            return user

        role = db.query(Role).filter(Role.name == "Administrator").first()
        if role is None:
            role = Role(
                name="Administrator",
                description="Built-in system administrator role",
                permissions="*",
                is_active=True,
            )
            db.add(role)
            db.flush()

        user = User(
            username=settings.DEFAULT_ADMIN_USERNAME,
            full_name=settings.DEFAULT_ADMIN_FULL_NAME,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.warning(
            "default administrator created username=%s; change the password after first login",
            user.username,
        )
        return user
