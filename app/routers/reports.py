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
from app.utils.jalali import to_jalali, get_today_jalali, parse_jalali_date

router = APIRouter(prefix="/reports", tags=["Reports"])
templates = create_templates()

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

    if customer_id:
        report = ReportService.get_customer_statement(db, customer_id, parse_jalali_date(from_date), parse_jalali_date(to_date))
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
            **report_data
        }
    )

@router.get("/customer-statement/excel")
async def customer_statement_excel(
    customer_id: int = Query(...), from_date: Optional[str] = Query(None), to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    report = ReportService.get_customer_statement(db, customer_id, parse_jalali_date(from_date), parse_jalali_date(to_date))
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])

    # ایجاد DataFrame
    data = []
    for t in report["transactions"]:
        data.append({
            "تاریخ": t["date"],
            "نوع": t["source_type"],
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
            "اعتبارها": m["total_credits"],
            "دریافت‌های قطعی": m["total_receipts"],
            "مانده": m["net_balance"]
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

    if account_id:
        report = ReportService.get_bank_report(db, account_id, parse_jalali_date(from_date), parse_jalali_date(to_date))
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

    if account_id:
        report = ReportService.get_bank_reconciliation(db, account_id)
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

# ============================================================
# خروجی PDF رسمی
# ============================================================
@router.get("/customer-statement/pdf")
async def customer_statement_pdf(customer_id: int = Query(...), db: Session = Depends(get_db)):
    from weasyprint import HTML
    report = ReportService.get_customer_statement(db, customer_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    rows = "".join(f"<tr><td>{item['date']}</td><td>{item['description']}</td><td>{item['debit']:,}</td><td>{item['credit']:,}</td><td>{item['balance']:,}</td></tr>" for item in report["transactions"])
    html = f"<html dir='rtl'><meta charset='utf-8'><h2>صورت‌حساب عضو: {report['customer'].full_name}</h2><p>مانده بدهی: {report['net_balance']:,} ریال</p><table border='1'><tr><th>تاریخ</th><th>شرح</th><th>بدهکار</th><th>بستانکار</th><th>مانده</th></tr>{rows}</table></html>"
    return StreamingResponse(io.BytesIO(HTML(string=html).write_pdf()), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=customer_statement_{customer_id}.pdf"})

@router.get("/project-summary/pdf")
async def project_summary_pdf(project_id: int = Query(...), db: Session = Depends(get_db)):
    from weasyprint import HTML
    report = ReportService.get_project_financial_summary(db, project_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    rows = "".join(f"<tr><td>{item['customer_no']}</td><td>{item['full_name']}</td><td>{item['net_balance']:,}</td></tr>" for item in report["member_summaries"])
    html = f"<html dir='rtl'><meta charset='utf-8'><h2>خلاصه مالی پروژه: {report['project'].name}</h2><p>جمع بدهی: {report['total_obligations']:,} ریال</p><table border='1'><tr><th>شماره عضو</th><th>نام</th><th>مانده</th></tr>{rows}</table></html>"
    return StreamingResponse(io.BytesIO(HTML(string=html).write_pdf()), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=project_summary_{project_id}.pdf"})

@router.get("/member-debt/excel")
async def member_debt_excel(project_id: int = Query(...), db: Session = Depends(get_db)):
    report = ReportService.get_project_financial_summary(db, project_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    rows = [item for item in report["member_summaries"] if item["net_balance"] > 0]
    df = pd.DataFrame([{"شماره عضو": item["customer_no"], "نام": item["full_name"], "مانده بدهی": item["net_balance"]} for item in rows])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer: df.to_excel(writer, index=False, sheet_name="بدهکاران")
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=member_debt_{project_id}.xlsx"})

@router.get("/member-debt/pdf")
async def member_debt_pdf(project_id: int = Query(...), db: Session = Depends(get_db)):
    from weasyprint import HTML
    report = ReportService.get_project_financial_summary(db, project_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    rows = "".join(f"<tr><td>{item['customer_no']}</td><td>{item['full_name']}</td><td>{item['net_balance']:,}</td></tr>" for item in report["member_summaries"] if item["net_balance"] > 0)
    html = f"<html dir='rtl'><meta charset='utf-8'><h2>گزارش بدهکاران: {report['project'].name}</h2><table border='1'><tr><th>شماره عضو</th><th>نام</th><th>مانده بدهی</th></tr>{rows}</table></html>"
    return StreamingResponse(io.BytesIO(HTML(string=html).write_pdf()), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=member_debt_{project_id}.pdf"})
