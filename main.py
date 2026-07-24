from fastapi import FastAPI
from app.core.config import settings
from app.routers import (
    customer_router,
    project_router,
    project_member_router,
    contract_router,
    financial_obligation_router,
    financial_credit_router,
    pages_router,
    bulk_import_router
)
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

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

# Page Routes (HTML)
app.include_router(pages_router)

# Bulk Import Routes
app.include_router(bulk_import_router)

@app.get("/")
async def root():
    return {
        "message": "Bonyan Core API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}