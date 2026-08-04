from contextlib import asynccontextmanager
import logging
import time
from urllib.parse import quote
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.routers.reports import router as reports_router
from app.routers.auth import router as auth_router
from app.core.audit import (
    register_audit_listeners,
    reset_audit_context,
    set_audit_context,
)
from app.core.auth import get_request_token, resolve_user_from_token
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging_config import configure_logging
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
    transfer_router,
    receipt_router,
)
from app.core.templates import create_templates
from app.services.bootstrap_service import BootstrapService

# Import all model modules before creating tables so SQLAlchemy metadata
# contains every mapped table, not just models imported indirectly by routers.
import app.models  # noqa: F401

logger = configure_logging(settings.LOG_LEVEL, settings.LOG_FILE)
register_audit_listeners()
templates = create_templates()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.AUTO_CREATE_SCHEMA:
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        BootstrapService.ensure_default_admin(db)
    logger.info("application startup complete version=%s", settings.APP_VERSION)
    yield
    logger.info("application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


PUBLIC_PATHS = {
    "/auth/login",
    "/auth/login-page",
    "/health",
    "/favicon.ico",
}


def _expects_html(request: Request) -> bool:
    if "text/html" in request.headers.get("accept", ""):
        return True
    return not (
        request.url.path.startswith("/api/")
        or request.url.path == "/openapi.json"
    )


@app.middleware("http")
async def authenticate_and_log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    request.state.request_id = request_id
    client_ip = request.client.host if request.client else None
    current_user = None
    audit_token = None
    response = None

    try:
        if request.url.path not in PUBLIC_PATHS and request.method != "OPTIONS":
            with SessionLocal() as db:
                current_user = resolve_user_from_token(
                    db,
                    get_request_token(request),
                )
            if current_user is None:
                if _expects_html(request):
                    next_url = quote(
                        request.url.path
                        + (f"?{request.url.query}" if request.url.query else ""),
                        safe="/?=&",
                    )
                    response = RedirectResponse(
                        f"/auth/login?next={next_url}",
                        status_code=303,
                    )
                else:
                    response = JSONResponse(
                        {"detail": "برای دسترسی به این بخش وارد سامانه شوید"},
                        status_code=401,
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return response

            request.state.user = current_user

        audit_token = set_audit_context(
            user_id=current_user.id if current_user else None,
            username=current_user.username if current_user else None,
            ip_address=client_ip,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        logger.exception(
            "request failed request_id=%s method=%s path=%s user=%s ip=%s",
            request_id,
            request.method,
            request.url.path,
            current_user.username if current_user else "-",
            client_ip or "-",
        )
        raise
    finally:
        if audit_token is not None:
            reset_audit_context(audit_token)
        duration_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "request request_id=%s method=%s path=%s status=%s duration_ms=%.2f user=%s ip=%s",
            request_id,
            request.method,
            request.url.path,
            getattr(response, "status_code", 500),
            duration_ms,
            current_user.username if current_user else "-",
            client_ip or "-",
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
app.include_router(transfer_router)
app.include_router(receipt_router)
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
    return RedirectResponse("/pages/", status_code=303)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
