from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from app.core.database import get_db
from app.services.bulk_import_service import BulkImportService
from app.services.excel_service import ExcelService
from app.services.project_service import ProjectService
from app.schemas.bulk_import import BulkImportCreate, BulkImportRow, BulkImportType, DebitType, CreditType as CreditTypeEnum
from app.models.bulk_import import BulkImportLog

router = APIRouter(prefix="/bulk-import", tags=["Bulk Import"])
templates = Jinja2Templates(directory="app/templates")

# ============================================================
# صفحه اصلی Bulk Import
# ============================================================
@router.get("/", response_class=HTMLResponse)
async def bulk_import_main(request: Request, db: Session = Depends(get_db)):
    projects = ProjectService.get_all(db)
    return templates.TemplateResponse(
        "bulk_import.html",
        {
            "request": request,
            "projects": projects,
            "import_types": [
                {"value": "DEBIT", "label": "بدهکار گروهی"},
                {"value": "CREDIT", "label": "بستانکار گروهی"},
                {"value": "MEMBER", "label": "اعضای پروژه"},
            ],
            "debit_types": [
                {"value": "PROJECT_PLAN", "label": "پلن پروژه"},
                {"value": "UNIT_DIFFERENCE", "label": "مابه‌التفاوت"},
                {"value": "PENALTY", "label": "جریمه"},
                {"value": "SERVICE_FEE", "label": "هزینه خدمات"},
                {"value": "OTHER", "label": "سایر"},
            ],
            "credit_types": [
                {"value": "LOAN", "label": "وام"},
                {"value": "SUBSIDY", "label": "سوبسید"},
                {"value": "DISCOUNT", "label": "تخفیف"},
                {"value": "CHEQUE", "label": "چک"},
                {"value": "OTHER", "label": "سایر"},
            ]
        }
    )

# ============================================================
# دانلود قالب Excel
# ============================================================
@router.get("/template/{import_type}")
async def download_template(import_type: str):
    """دانلود قالب Excel بر اساس نوع عملیات"""
    excel_data = ExcelService.generate_template(import_type)
    
    filename = f"template_{import_type}.xlsx"
    return StreamingResponse(
        iter([excel_data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ============================================================
# آپلود و پردازش فایل Excel
# ============================================================
@router.post("/upload")
async def upload_excel(
    request: Request,
    file: UploadFile = File(...),
    import_type: str = Form(...),
    project_id: int = Form(...),
    document_date: str = Form(...),
    document_description: str = Form(...),
    debit_type: Optional[str] = Form(None),
    credit_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """آپلود فایل Excel و نمایش پیش‌نمایش"""
    try:
        # خواندن فایل
        content = await file.read()
        rows, errors = ExcelService.parse_excel(content)
        
        if errors:
            return templates.TemplateResponse(
                "bulk_import_preview.html",
                {
                    "request": request,
                    "errors": errors,
                    "rows": [],
                    "import_type": import_type,
                    "project_id": project_id,
                    "document_date": document_date,
                    "document_description": document_description,
                    "debit_type": debit_type,
                    "credit_type": credit_type,
                    "total_rows": 0,
                    "total_amount": 0
                }
            )
        
        # محاسبه جمع کل
        total_amount = sum([row.get("amount", 0) or 0 for row in rows])
        
        return templates.TemplateResponse(
            "bulk_import_preview.html",
            {
                "request": request,
                "errors": [],
                "rows": rows,
                "import_type": import_type,
                "project_id": project_id,
                "document_date": document_date,
                "document_description": document_description,
                "debit_type": debit_type,
                "credit_type": credit_type,
                "total_rows": len(rows),
                "total_amount": total_amount
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "bulk_import_preview.html",
            {
                "request": request,
                "errors": [str(e)],
                "rows": [],
                "import_type": import_type,
                "project_id": project_id,
                "document_date": document_date,
                "document_description": document_description,
                "debit_type": debit_type,
                "credit_type": credit_type,
                "total_rows": 0,
                "total_amount": 0
            }
        )

# ============================================================
# ذخیره نهایی داده‌های Import
# ============================================================
@router.post("/save")
async def save_bulk_import(
    request: Request,
    db: Session = Depends(get_db)
):
    """ذخیره نهایی داده‌های Import شده"""
    try:
        # دریافت داده‌ها از فرم
        form_data = await request.form()
        
        import_type = form_data.get("import_type")
        project_id = int(form_data.get("project_id"))
        document_date = form_data.get("document_date")
        document_description = form_data.get("document_description")
        debit_type = form_data.get("debit_type")
        credit_type = form_data.get("credit_type")
        
        # دریافت ردیف‌ها
        rows_data = []
        row_count = int(form_data.get("row_count", 0))
        
        for i in range(row_count):
            member_no = form_data.get(f"rows[{i}][member_no]")
            if not member_no:
                continue
                
            row = {
                "member_no": member_no,
                "full_name": form_data.get(f"rows[{i}][full_name]"),
                "amount": int(form_data.get(f"rows[{i}][amount]", 0)) if form_data.get(f"rows[{i}][amount]") else None,
                "description": form_data.get(f"rows[{i}][description]")
            }
            rows_data.append(row)
        
        # ساخت داده‌های BulkImportCreate
        from datetime import datetime
        from app.schemas.bulk_import import BulkImportCreate, BulkImportRow
        
        bulk_rows = []
        for row in rows_data:
            bulk_rows.append(BulkImportRow(
                member_no=row["member_no"],
                full_name=row.get("full_name"),
                amount=row.get("amount"),
                description=row.get("description")
            ))
        
        data = BulkImportCreate(
            import_type=import_type,
            project_id=project_id,
            document_date=datetime.strptime(document_date, "%Y-%m-%d").date(),
            document_description=document_description,
            debit_type=debit_type,
            credit_type=credit_type,
            rows=bulk_rows
        )
        
        # پردازش داده‌ها
        result = BulkImportService.process_bulk_import(db, data)
        
        # ثبت لاگ
        log = BulkImportLog(
            import_type=import_type,
            project_id=project_id,
            journal_no=result.get("journal_no"),
            total_rows=result.get("total_rows", 0),
            total_amount=result.get("total_amount", 0),
            status="SUCCESS" if result.get("success") else "FAILED",
            message=result.get("message"),
            errors=json.dumps(result.get("errors", [])) if result.get("errors") else None
        )
        db.add(log)
        db.commit()
        
        if result.get("success"):
            return templates.TemplateResponse(
                "bulk_import_success.html",
                {
                    "request": request,
                    "message": result.get("message"),
                    "journal_no": result.get("journal_no"),
                    "total_rows": result.get("total_rows"),
                    "total_amount": result.get("total_amount")
                }
            )
        else:
            return templates.TemplateResponse(
                "bulk_import_preview.html",
                {
                    "request": request,
                    "errors": result.get("errors", []),
                    "rows": [],
                    "import_type": import_type,
                    "project_id": project_id,
                    "document_date": document_date,
                    "document_description": document_description,
                    "debit_type": debit_type,
                    "credit_type": credit_type,
                    "total_rows": 0,
                    "total_amount": 0,
                    "error_message": result.get("message")
                }
            )
            
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "bulk_import_preview.html",
            {
                "request": request,
                "errors": [str(e)],
                "rows": [],
                "import_type": form_data.get("import_type") if 'form_data' in locals() else "DEBIT",
                "project_id": int(form_data.get("project_id")) if 'form_data' in locals() and form_data.get("project_id") else None,
                "document_date": form_data.get("document_date") if 'form_data' in locals() else "",
                "document_description": form_data.get("document_description") if 'form_data' in locals() else "",
                "debit_type": form_data.get("debit_type") if 'form_data' in locals() else None,
                "credit_type": form_data.get("credit_type") if 'form_data' in locals() else None,
                "total_rows": 0,
                "total_amount": 0,
                "error_message": str(e)
            }
        )

# ============================================================
# تاریخچه Import
# ============================================================
@router.get("/history", response_class=HTMLResponse)
async def import_history(request: Request, db: Session = Depends(get_db)):
    logs = db.query(BulkImportLog).filter(
        BulkImportLog.is_deleted == False
    ).order_by(BulkImportLog.created_at.desc()).limit(100).all()
    
    return templates.TemplateResponse(
        "bulk_import_history.html",
        {
            "request": request,
            "logs": logs
        }
    )