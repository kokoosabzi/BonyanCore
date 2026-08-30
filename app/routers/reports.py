from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import io
import pandas as pd
from datetime import date

from app.core.database import get_db
from app.services.report_service import ReportService
from app.services.customer_service import CustomerService
from app.services.project_service import ProjectService
from app.services.bank_account_service import BankAccountService
from app.core.templates import create_templates
from app.utils.jalali import get_today_jalali, parse_jalali_date, to_jalali
from app.models.financial_obligation import FinancialObligation

router = APIRouter(prefix="/reports", tags=["Reports"])
templates = create_templates()


def _parse_date_filters(
    from_date: Optional[str], to_date: Optional[str]
) -> tuple[Optional[date], Optional[date], Optional[str]]:
    """Parse Jalali report filters without turning invalid form input into a 500."""
    try:
        parsed_from = parse_jalali_date(from_date)
        parsed_to = parse_jalali_date(to_date)
        ReportService._validate_date_range(parsed_from, parsed_to)
        return parsed_from, parsed_to, None
    except ValueError as exc:
        return None, None, str(exc)

# ============================================================
# داشبورد مالی
# ============================================================
@router.get("/dashboard", response_class=HTMLResponse)
async def financial_dashboard(request: Request, db: Session = Depends(get_db)):
    """داشبورد مالی"""
    return templates.TemplateResponse(
        "reports/dashboard_financial.html",
        {
            "request": request,
            "active_page": "reports",
            "today": get_today_jalali()
        }
    )

# ============================================================
# صورت حساب مشتری
# ============================================================
@router.get("/customer-statement", response_class=HTMLResponse)
async def customer_statement_page(
    request: Request,
    customer_id: Optional[int] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    customers = CustomerService.get_all(db)
    report_data = {}

    parsed_from, parsed_to, date_error = _parse_date_filters(from_date, to_date)
    if customer_id and not date_error:
        report = ReportService.get_customer_statement(db, customer_id, parsed_from, parsed_to)
        if "error" not in report:
            report_data = report

    return templates.TemplateResponse(
        "reports/customer_statement.html",
        {
            "request": request,
            "active_page": "reports",
            "customers": customers,
            "customer_id": customer_id,
            "from_date": from_date,
            "to_date": to_date,
            "date_error": date_error,
            **report_data
        }
    )

@router.get("/customer-statement/excel")
async def customer_statement_excel(
    customer_id: int = Query(...),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    parsed_from, parsed_to, date_error = _parse_date_filters(from_date, to_date)
    if date_error:
        raise HTTPException(status_code=422, detail=date_error)
    report = ReportService.get_customer_statement(db, customer_id, parsed_from, parsed_to)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])

    # ایجاد DataFrame
    data = [{
        "تاریخ": to_jalali(parsed_from) if parsed_from else "",
        "نوع": "OPENING_BALANCE",
        "شرح": "مانده ابتدای دوره",
        "بدهکار": report["opening_debit"],
        "بستانکار": report["opening_credit"],
        "مانده": report["opening_balance"],
    }]
    for t in report["transactions"]:
        data.append({
            "تاریخ": to_jalali(t["date"]),
            "نوع": t["type"],
            "شرح": t["description"],
            "بدهکار": t["debit"],
            "بستانکار": t["credit"],
            "مانده": t["balance"]
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="صورت حساب")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=customer_statement_{customer_id}.xlsx"}
    )

# ============================================================
# خلاصه مالی پروژه
# ============================================================
@router.get("/project-summary", response_class=HTMLResponse)
async def project_summary_page(
    request: Request,
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    projects = ProjectService.get_all(db)
    report_data = {}

    if project_id:
        report = ReportService.get_project_financial_summary(db, project_id)
        if "error" not in report:
            report_data = report

    return templates.TemplateResponse(
        "reports/project_summary.html",
        {
            "request": request,
            "active_page": "reports",
            "projects": projects,
            "project_id": project_id,
            **report_data
        }
    )

@router.get("/project-summary/excel")
async def project_summary_excel(
    project_id: int = Query(...),
    db: Session = Depends(get_db)
):
    report = ReportService.get_project_financial_summary(db, project_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])

    data = []
    for m in report.get("member_summaries", []):
        data.append({
            "شماره عضو": m["customer_no"],
            "نام": m["full_name"],
            "کل بدهی": m["total_obligations"],
            "کل پرداخت": m["total_credits"],
            "مانده": m["balance"]
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="خلاصه مالی")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=project_summary_{project_id}.xlsx"}
    )

# ============================================================
# گزارش بانک
# ============================================================
@router.get("/bank", response_class=HTMLResponse)
async def bank_report_page(
    request: Request,
    account_id: Optional[int] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    accounts = BankAccountService.get_all(db)
    report_data = {}

    parsed_from, parsed_to, date_error = _parse_date_filters(from_date, to_date)
    if account_id and not date_error:
        report = ReportService.get_bank_report(db, account_id, parsed_from, parsed_to)
        if "error" not in report:
            report_data = report

    return templates.TemplateResponse(
        "reports/bank_report.html",
        {
            "request": request,
            "active_page": "reports",
            "accounts": accounts,
            "account_id": account_id,
            "from_date": from_date,
            "to_date": to_date,
            "date_error": date_error,
            **report_data
        }
    )

# ============================================================
# گزارش مغایرت بانکی
# ============================================================
@router.get("/bank-reconciliation", response_class=HTMLResponse)
async def bank_reconciliation_page(
    request: Request,
    account_id: Optional[int] = Query(None),
    statement_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    accounts = BankAccountService.get_all(db)
    report_data = {}

    try:
        parsed_statement_date = parse_jalali_date(statement_date)
        date_error = None
    except ValueError as exc:
        parsed_statement_date = None
        date_error = str(exc)

    if account_id and not date_error:
        report = ReportService.get_bank_reconciliation(db, account_id, parsed_statement_date)
        if "error" not in report:
            report_data = report

    return templates.TemplateResponse(
        "reports/bank_reconciliation.html",
        {
            "request": request,
            "active_page": "reports",
            "accounts": accounts,
            "account_id": account_id,
            "statement_date": statement_date,
            "date_error": date_error,
            **report_data
        }
    )

# ============================================================
# گزارش بدهکاران
# ============================================================
@router.get("/member-debt", response_class=HTMLResponse)
async def member_debt_page(
    request: Request,
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    projects = ProjectService.get_all(db)
    debts = []

    if project_id:
        obligations = db.query(FinancialObligation).filter(
            FinancialObligation.project_id == project_id,
            FinancialObligation.status != "PAID",
            FinancialObligation.is_deleted == False
        ).all()
        debts = obligations

    return templates.TemplateResponse(
        "reports/member_debt.html",
        {
            "request": request,
            "active_page": "reports",
            "projects": projects,
            "project_id": project_id,
            "debts": debts
        }
    )
