import logging
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.auth import (
    get_current_user,
    get_request_token,
    require_superuser,
    resolve_user_from_token,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.core.templates import create_templates
from app.schemas.auth import UserCreate, UserLogin, UserResponse, ChangePassword
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = create_templates()
logger = logging.getLogger("bonyancore.auth")


def _safe_next_url(value: str | None) -> str:
    if not value:
        return "/pages/"
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not value.startswith("/"):
        return "/pages/"
    return value

# ============================================================
# API Routes
# ============================================================
@router.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """ورود کاربر"""
    user = AuthService.authenticate(db, data.username, data.password)
    if not user:
        logger.warning("api login failed username=%s", data.username)
        raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")
    
    token = create_access_token({"sub": user.username, "user_id": user.id})
    logger.info("api login succeeded username=%s user_id=%s", user.username, user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.post("/register", response_model=UserResponse)
async def register(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """ثبت نام کاربر جدید"""
    try:
        user = AuthService.create_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-password")
async def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """تغییر رمز عبور"""
    try:
        AuthService.change_password(db, current_user.id, data)
        return {"message": "رمز عبور با موفقیت تغییر کرد"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """صفحه ثبت نام"""
    roles = RoleService.get_all(db)
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "roles": roles, "error": None}
    )

@router.post("/register-page")
async def register_page_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(""),
    role_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """ثبت نام از طریق صفحه HTML"""
    try:
        data = UserCreate(
            username=username,
            password=password,
            full_name=full_name,
            phone=phone if phone else None,
            role_id=role_id
        )
        AuthService.create_user(db, data)
        return RedirectResponse("/auth/users", status_code=303)
    except ValueError as e:
        roles = RoleService.get_all(db)
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "roles": roles, "error": str(e)},
            status_code=400,
        )


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    next: Optional[str] = None,
    db: Session = Depends(get_db),
):
    existing_user = resolve_user_from_token(db, get_request_token(request))
    if existing_user:
        return RedirectResponse(_safe_next_url(next), status_code=303)
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "error": None,
            "next_url": _safe_next_url(next),
        },
    )


@router.post("/login-page")
async def login_page_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/pages/"),
    db: Session = Depends(get_db),
):
    user = AuthService.authenticate(db, username, password)
    if not user:
        logger.warning(
            "browser login failed username=%s ip=%s",
            username,
            request.client.host if request.client else "-",
        )
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "نام کاربری یا رمز عبور اشتباه است",
                "next_url": _safe_next_url(next_url),
            },
            status_code=401,
        )

    token = create_access_token({"sub": user.username, "user_id": user.id})
    response = RedirectResponse(_safe_next_url(next_url), status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    logger.info(
        "browser login succeeded username=%s user_id=%s ip=%s",
        user.username,
        user.id,
        request.client.host if request.client else "-",
    )
    return response


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    response = RedirectResponse("/auth/login", status_code=303)
    response.delete_cookie("access_token", path="/")
    logger.info(
        "logout username=%s user_id=%s ip=%s",
        current_user.username,
        current_user.id,
        request.client.host if request.client else "-",
    )
    return response


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """صفحه پروفایل کاربر"""
    return templates.TemplateResponse(
        "auth/profile.html",
        {"request": request, "user": current_user},
    )


@router.post("/change-password-page", response_class=HTMLResponse)
async def change_password_page(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        data = ChangePassword(
            old_password=old_password,
            new_password=new_password,
            confirm_password=confirm_password,
        )
        AuthService.change_password(db, current_user.id, data)
        return templates.TemplateResponse(
            "auth/profile.html",
            {
                "request": request,
                "user": current_user,
                "success": "رمز عبور با موفقیت تغییر کرد",
            },
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            "auth/profile.html",
            {
                "request": request,
                "user": current_user,
                "error": str(exc),
            },
            status_code=400,
        )


@router.get("/users", response_class=HTMLResponse)
async def user_list(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """لیست کاربران"""
    users = AuthService.get_all(db)
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "users": users}
    )

@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def user_edit_form(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """فرم ویرایش کاربر"""
    user = AuthService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر پیدا نشد")
    roles = RoleService.get_all(db)
    return templates.TemplateResponse(
        "admin/user_edit.html",
        {"request": request, "user": user, "roles": roles}
    )

@router.post("/users/{user_id}/edit")
async def user_edit(
    user_id: int,
    full_name: str = Form(...),
    phone: str = Form(""),
    is_active: bool = Form(False),
    role_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """ویرایش کاربر"""
    from app.schemas.auth import UserUpdate
    data = UserUpdate(
        full_name=full_name,
        phone=phone if phone else None,
        is_active=is_active,
        role_id=role_id
    )
    try:
        target = AuthService.get_by_id(db, user_id)
        if not target:
            raise HTTPException(status_code=404, detail="کاربر پیدا نشد")
        AuthService.validate_account_state_change(
            db,
            target,
            actor_user_id=current_user.id,
            will_be_active=is_active,
        )
        if not AuthService.update(db, user_id, data):
            raise HTTPException(status_code=404, detail="کاربر پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/auth/users", status_code=303)

@router.post("/users/{user_id}/delete")
async def user_delete(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """حذف کاربر"""
    target = AuthService.get_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="کاربر پیدا نشد")
    try:
        AuthService.validate_account_state_change(
            db,
            target,
            actor_user_id=current_user.id,
            will_be_active=False,
            deleting=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not AuthService.delete(db, user_id):
        raise HTTPException(status_code=404, detail="کاربر پیدا نشد")
    return RedirectResponse("/auth/users", status_code=303)


@router.get("/audit-logs", response_class=HTMLResponse)
async def audit_log_list(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(500).all()
    return templates.TemplateResponse(
        "admin/audit_logs.html",
        {"request": request, "logs": logs},
    )
