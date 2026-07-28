from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.routers.reports import router as reports_router
from app.routers.auth import router as auth_router
from app.core.config import settings
from app.routers import (
    customer_router,
    project_router,
    project_member_router,
    contract_router,
    financial_obligation_router,
    financial_credit_router,
    pages_router,
    bulk_import_router,
    journal_entry_router,
    cheque_book_router,
)
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# API Routes
app.include_router(customer_router)
app.include_router(project_router)
app.include_router(project_member_router)
app.include_router(contract_router)
app.include_router(financial_obligation_router)
app.include_router(financial_credit_router)
app.include_router(journal_entry_router)
app.include_router(cheque_book_router)
app.include_router(auth_router)
app.include_router(reports_router)
# Page Routes
app.include_router(pages_router)
# Bulk Import Routes
app.include_router(bulk_import_router)

@app.get("/intro")
async def intro_page(request: Request):
    return templates.TemplateResponse("intro.html", {"request": request})

@app.get("/")
async def root():
    return {
        "message": "Bonyan Core API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "intro": "/intro"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}