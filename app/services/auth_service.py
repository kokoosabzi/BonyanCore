from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserCreate, UserUpdate, ChangePassword
from app.utils.security import verify_password, get_password_hash
from datetime import datetime

class AuthService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        """احراز هویت کاربر"""
        user = db.query(User).filter(
            User.username == username,
            User.is_active == True,
            User.is_deleted == False
        ).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        user.last_login = datetime.now()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        """ایجاد کاربر جدید"""
        # بررسی تکراری نبودن نام کاربری
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise ValueError("نام کاربری قبلاً ثبت شده است")
        
        if data.role_id:
            role = db.query(Role).filter(
                Role.id == data.role_id,
                Role.is_active.is_(True),
                Role.is_deleted.is_(False),
            ).first()
            if not role:
                raise ValueError("نقش انتخاب‌شده معتبر نیست")
        
        user = User(
            username=data.username,
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=get_password_hash(data.password),
            role_id=data.role_id,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).filter(
            User.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, user_id: int, data: UserUpdate) -> User | None:
        user = AuthService.get_by_id(db, user_id)
        if not user:
            return None
        update_data = data.model_dump(exclude_unset=True)
        role_id = update_data.get("role_id")
        if role_id:
            role = db.query(Role).filter(
                Role.id == role_id,
                Role.is_active.is_(True),
                Role.is_deleted.is_(False),
            ).first()
            if not role:
                raise ValueError("نقش انتخاب‌شده معتبر نیست")
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user_id: int, data: ChangePassword) -> bool:
        user = AuthService.get_by_id(db, user_id)
        if not user:
            return False
        # بررسی رمز عبور قدیمی
        if not verify_password(data.old_password, user.hashed_password):
            raise ValueError("رمز عبور فعلی صحیح نیست")
        # ذخیره رمز جدید
        user.hashed_password = get_password_hash(data.new_password)
        db.commit()
        return True

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        user = AuthService.get_by_id(db, user_id)
        if not user:
            return False
        user.is_deleted = True
        user.is_active = False
        user.deleted_at = datetime.now()
        db.commit()
        return True

    @staticmethod
    def count_active_superusers(db: Session) -> int:
        return db.query(User).filter(
            User.is_superuser.is_(True),
            User.is_active.is_(True),
            User.is_deleted.is_(False),
        ).count()

    @staticmethod
    def validate_account_state_change(
        db: Session,
        target: User,
        actor_user_id: int,
        will_be_active: bool,
        deleting: bool = False,
    ) -> None:
        if target.id == actor_user_id and (deleting or not will_be_active):
            raise ValueError("امکان حذف یا غیرفعال‌کردن حساب کاربری جاری وجود ندارد")
        if (
            target.is_superuser
            and (deleting or not will_be_active)
            and AuthService.count_active_superusers(db) <= 1
        ):
            raise ValueError("آخرین مدیر فعال سامانه قابل حذف یا غیرفعال‌کردن نیست")

    @staticmethod
    def create_superuser(db: Session, username: str, password: str, full_name: str, email: str = None) -> User:
        """ایجاد کاربر ادمین"""
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("نام کاربری قبلاً ثبت شده است")
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> list:
        """دریافت مجوزهای کاربر"""
        user = AuthService.get_by_id(db, user_id)
        if not user:
            return []
        if user.is_superuser:
            return ["*"]  # دسترسی کامل
        
        permissions = []
        if user.role_id:
            role = db.query(Role).filter(Role.id == user.role_id).first()
            if role and role.permissions:
                permissions = role.permissions.split(',')
        return permissions
