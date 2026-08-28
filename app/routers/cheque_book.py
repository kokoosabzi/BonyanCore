from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.schemas.cheque_book import ChequeBookCreate, ChequeBookUpdate, ChequeBookResponse
from app.services.cheque_book_service import ChequeBookService
from app.services.bank_account_service import BankAccountService
from app.core.templates import create_templates

router = APIRouter(prefix="/api/v1/cheque-books", tags=["Cheque Books"])
templates = create_templates()

# ============================================================
# API Routes
# ============================================================
@router.post("/", response_model=ChequeBookResponse, status_code=status.HTTP_201_CREATED)
def create_cheque_book(data: ChequeBookCreate, db: Session = Depends(get_db)):
    try:
        return ChequeBookService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ChequeBookResponse])
def get_cheque_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return ChequeBookService.get_all(db, skip, limit)

@router.get("/{book_id}", response_model=ChequeBookResponse)
def get_cheque_book(book_id: int, db: Session = Depends(get_db)):
    book = ChequeBookService.get_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="دسته چک پیدا نشد")
    return book

@router.put("/{book_id}", response_model=ChequeBookResponse)
def update_cheque_book(book_id: int, data: ChequeBookUpdate, db: Session = Depends(get_db)):
    try:
        book = ChequeBookService.update(db, book_id, data)
        if not book:
            raise HTTPException(status_code=404, detail="دسته چک پیدا نشد")
        return book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cheque_book(book_id: int, db: Session = Depends(get_db)):
    try:
        if not ChequeBookService.delete(db, book_id):
            raise HTTPException(status_code=404, detail="دسته چک پیدا نشد")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{book_id}/use-cheque/{cheque_id}")
def use_cheque(
    book_id: int,
    cheque_id: int,
    receipt_id: int = Query(...),
    db: Session = Depends(get_db)
):
    try:
        cheque = ChequeBookService.use_cheque(db, cheque_id, receipt_id)
        if not cheque:
            raise HTTPException(status_code=404, detail="چک پیدا نشد")
        return {"message": "چک با موفقیت استفاده شد", "cheque": cheque}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================
# Page Routes (HTML)
# ============================================================
@router.get("/create", response_class=HTMLResponse)
async def cheque_book_create_form(request: Request, db: Session = Depends(get_db)):
    bank_accounts = BankAccountService.get_all(db)
    return templates.TemplateResponse(
        "cheque_book_form.html",
        {
            "request": request,
            "active_page": "cheque",
            "bank_accounts": bank_accounts,
            "book": None
        }
    )

@router.get("/list", response_class=HTMLResponse)
async def cheque_book_list(request: Request, db: Session = Depends(get_db)):
    books = ChequeBookService.get_all(db, limit=100)
    return templates.TemplateResponse(
        "cheque_book_list.html",
        {
            "request": request,
            "active_page": "cheque",
            "books": books
        }
    )

@router.get("/{book_id}/edit", response_class=HTMLResponse)
async def cheque_book_edit_form(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = ChequeBookService.get_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="دسته چک پیدا نشد")
    bank_accounts = BankAccountService.get_all(db)
    return templates.TemplateResponse(
        "cheque_book_form.html",
        {
            "request": request,
            "active_page": "cheque",
            "bank_accounts": bank_accounts,
            "book": book
        }
    )
