from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import jwt

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.core.templates import create_templates
from app.schemas.auth import UserCreate, UserLogin, UserResponse, ChangePassword
from app.utils.security import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = create_templates()

# ============================================================
# API Routes
# ============================================================
@router.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """ورود کاربر"""
    user = AuthService.authenticate(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")
    
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    """ثبت نام کاربر جدید"""
    try:
        user = AuthService.create_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-password")
async def change_password(
    user_id: int,
    data: ChangePassword,
    db: Session = Depends(get_db)
):
    """تغییر رمز عبور"""
    try:
        AuthService.change_password(db, user_id, data)
        return {"message": "رمز عبور با موفقیت تغییر کرد"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================
# Page Routes (HTML)
# ============================================================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """صفحه ورود"""
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})

@router.post("/login-page")
async def login_page_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """ورود از طریق صفحه HTML"""
    user = AuthService.authenticate(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "نام کاربری یا رمز عبور اشتباه است"}
        )
    token = create_access_token({"sub": user.username, "user_id": user.id})
    response = RedirectResponse("/pages/", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@router.get("/logout")
async def logout():
    """خروج از سیستم"""
    response = RedirectResponse("/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
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
    email: str = Form(""),
    phone: str = Form(""),
    role_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """ثبت نام از طریق صفحه HTML"""
    try:
        data = UserCreate(
            username=username,
            password=password,
            full_name=full_name,
            email=email if email else None,
            phone=phone if phone else None,
            role_id=role_id
        )
        AuthService.create_user(db, data)
        return RedirectResponse("/auth/login", status_code=303)
    except ValueError as e:
        roles = RoleService.get_all(db)
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "roles": roles, "error": str(e)}
        )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """صفحه پروفایل کاربر"""
    return templates.TemplateResponse("auth/profile.html", {"request": request})

@router.get("/users", response_class=HTMLResponse)
async def user_list(request: Request, db: Session = Depends(get_db)):
    """لیست کاربران"""
    users = AuthService.get_all(db)
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "users": users}
    )

@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def user_edit_form(request: Request, user_id: int, db: Session = Depends(get_db)):
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
    email: str = Form(""),
    phone: str = Form(""),
    is_active: bool = Form(True),
    role_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """ویرایش کاربر"""
    from app.schemas.auth import UserUpdate
    data = UserUpdate(
        full_name=full_name,
        email=email if email else None,
        phone=phone if phone else None,
        is_active=is_active,
        role_id=role_id
    )
    AuthService.update(db, user_id, data)
    return RedirectResponse("/auth/users", status_code=303)

@router.post("/users/{user_id}/delete")
async def user_delete(user_id: int, db: Session = Depends(get_db)):
    """حذف کاربر"""
    AuthService.delete(db, user_id)
    return RedirectResponse("/auth/users", status_code=303)
