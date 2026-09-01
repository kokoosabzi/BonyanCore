from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
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
from app.routers.receipt import router as receipt_router
from app.routers.payment import router as payment_router
from app.routers.bank_reconciliation import router as bank_reconciliation_router
from app.core.database import Base, engine
from app.core.templates import create_templates

# Import all model modules before creating tables so SQLAlchemy metadata
# contains every mapped table, not just models imported indirectly by routers.
import app.models  # noqa: F401

if settings.AUTO_CREATE_TABLES:
    Base.metadata.create_all(bind=engine)

templates = create_templates()

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
app.include_router(receipt_router)
app.include_router(payment_router)
app.include_router(bank_reconciliation_router)
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

@app.get("/health/db")
async def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "unreachable",
                "detail": exc.__class__.__name__,
            },
        )
    return {"status": "healthy", "database": "reachable"}
