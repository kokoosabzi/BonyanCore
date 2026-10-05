from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token


def get_request_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    scheme, _, credentials = authorization.partition(" ")
    if scheme.lower() == "bearer" and credentials:
        return credentials.strip()
    return request.cookies.get("access_token")


def resolve_user_from_token(db: Session, token: str | None) -> User | None:
    payload = decode_access_token(token) if token else None
    user_id = payload.get("user_id") if payload else None
    if not isinstance(user_id, int):
        return None
    return db.query(User).options(joinedload(User.role)).filter(
        User.id == user_id,
        User.is_active.is_(True),
        User.is_deleted.is_(False),
    ).first()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    current_user = getattr(request.state, "user", None)
    if current_user is None:
        current_user = resolve_user_from_token(db, get_request_token(request))
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="برای دسترسی به این بخش وارد سامانه شوید",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.user = current_user
    return current_user


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="این عملیات فقط برای مدیر سیستم مجاز است",
        )
    return current_user
