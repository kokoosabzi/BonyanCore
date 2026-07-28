from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse
from app.services.journal_entry_service import JournalEntryService
from app.services.account_service import AccountService

router = APIRouter(prefix="/api/v1/journal-entries", tags=["Journal Entries"])
templates = Jinja2Templates(directory="app/templates")

# ============================================================
# API Routes
# ============================================================
@router.post("/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry(data: JournalEntryCreate, db: Session = Depends(get_db)):
    try:
        return JournalEntryService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[JournalEntryResponse])
def get_journal_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return JournalEntryService.get_all(db, skip, limit, status)

@router.get("/{journal_id}", response_model=JournalEntryResponse)
def get_journal_entry(journal_id: int, db: Session = Depends(get_db)):
    journal = JournalEntryService.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="سند پیدا نشد")
    return journal

@router.put("/{journal_id}", response_model=JournalEntryResponse)
def update_journal_entry(journal_id: int, data: JournalEntryUpdate, db: Session = Depends(get_db)):
    try:
        journal = JournalEntryService.update(db, journal_id, data)
        if not journal:
            raise HTTPException(status_code=404, detail="سند پیدا نشد")
        return journal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{journal_id}/post", response_model=JournalEntryResponse)
def post_journal_entry(journal_id: int, db: Session = Depends(get_db)):
    try:
        journal = JournalEntryService.post(db, journal_id)
        if not journal:
            raise HTTPException(status_code=404, detail="سند پیدا نشد")
        return journal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(journal_id: int, db: Session = Depends(get_db)):
    try:
        if not JournalEntryService.delete(db, journal_id):
            raise HTTPException(status_code=404, detail="سند پیدا نشد")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================
# Page Routes (HTML)
# ============================================================
@router.get("/create", response_class=HTMLResponse)
async def journal_entry_create_form(request: Request, db: Session = Depends(get_db)):
    accounts = AccountService.get_all(db)
    return templates.TemplateResponse(
        "journal_entry_form.html",
        {
            "request": request,
            "active_page": "journal",
            "accounts": accounts,
            "journal": None
        }
    )

@router.get("/list", response_class=HTMLResponse)
async def journal_entry_list(request: Request, db: Session = Depends(get_db)):
    journals = JournalEntryService.get_all(db, limit=100)
    return templates.TemplateResponse(
        "journal_entry_list.html",
        {
            "request": request,
            "active_page": "journal",
            "journals": journals
        }
    )

@router.get("/{journal_id}/edit", response_class=HTMLResponse)
async def journal_entry_edit_form(request: Request, journal_id: int, db: Session = Depends(get_db)):
    journal = JournalEntryService.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="سند پیدا نشد")
    accounts = AccountService.get_all(db)
    return templates.TemplateResponse(
        "journal_entry_form.html",
        {
            "request": request,
            "active_page": "journal",
            "accounts": accounts,
            "journal": journal
        }
    )