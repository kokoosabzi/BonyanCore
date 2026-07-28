from fastapi import APIRouter, Depends, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.database import get_db
from app.services.bulk_import_service import BulkImportService
from app.services.excel_service import ExcelService
from app.services.project_service import ProjectService
from app.core.templates import create_templates
from app.schemas.bulk_import import BulkImportCreate, BulkImportRow
from app.models.bulk_import import BulkImportLog

router = APIRouter(prefix="/bulk-import", tags=["Bulk Import"])
templates = create_templates()

@router.get("/", response_class=HTMLResponse)
async def bulk_import_main(request: Request, db: Session = Depends(get_db)):
    projects = ProjectService.get_all(db)
    return templates.TemplateResponse(
        "bulk_import.html",
        {"request": request, "active_page": "bulk", "projects": projects}
    )

@router.get("/template/{import_type}")
async def download_template(import_type: str):
    data = ExcelService.generate_template(import_type)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=template_{import_type}.xlsx"}
    )

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
    try:
        content = await file.read()
        rows, errors = ExcelService.parse_excel(content)
        total_amount = sum([r.get("amount", 0) or 0 for r in rows])
        return templates.TemplateResponse("bulk_import_preview.html", {
            "request": request,
            "errors": errors,
            "rows": rows,
            "import_type": import_type,
            "project_id": project_id,
            "document_date": document_date,
            "document_description": document_description,
            "debit_type": debit_type,
            "credit_type": credit_type,
            "total_rows": len(rows),
            "total_amount": total_amount
        })
    except Exception as e:
        return templates.TemplateResponse("bulk_import_preview.html", {
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
        })

@router.post("/save")
async def save_bulk_import(request: Request, db: Session = Depends(get_db)):
    try:
        form = await request.form()
        rows_data = []
        for i in range(int(form.get("row_count", 0))):
            if form.get(f"rows[{i}][member_no]"):
                rows_data.append({
                    "member_no": form.get(f"rows[{i}][member_no]"),
                    "full_name": form.get(f"rows[{i}][full_name]"),
                    "amount": int(form.get(f"rows[{i}][amount]", 0)) if form.get(f"rows[{i}][amount]") else None,
                    "description": form.get(f"rows[{i}][description]")
                })
        
        data = BulkImportCreate(
            import_type=form.get("import_type"),
            project_id=int(form.get("project_id")),
            document_date=form.get("document_date"),
            document_description=form.get("document_description"),
            debit_type=form.get("debit_type"),
            credit_type=form.get("credit_type"),
            rows=[BulkImportRow(**r) for r in rows_data]
        )
        
        result = BulkImportService.process_bulk_import(db, data)
        log = BulkImportLog(
            import_type=form.get("import_type"),
            project_id=int(form.get("project_id")),
            journal_no=result.get("journal_no"),
            total_rows=result.get("total_rows", 0),
            total_amount=result.get("total_amount", 0),
            status="SUCCESS" if result.get("success") else "FAILED",
            message=result.get("message"),
            errors=json.dumps(result.get("errors", [])) if result.get("errors") else None
        )
        db.add(log)
        db.commit()
        
        return templates.TemplateResponse("bulk_import_success.html", {
            "request": request,
            "message": result.get("message"),
            "journal_no": result.get("journal_no"),
            "total_rows": result.get("total_rows"),
            "total_amount": result.get("total_amount")
        })
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("bulk_import_preview.html", {
            "request": request,
            "errors": [str(e)],
            "rows": [],
            "import_type": "DEBIT",
            "project_id": 0,
            "document_date": "",
            "document_description": "",
            "debit_type": None,
            "credit_type": None,
            "total_rows": 0,
            "total_amount": 0
        })

@router.get("/history", response_class=HTMLResponse)
async def import_history(request: Request, db: Session = Depends(get_db)):
    logs = db.query(BulkImportLog).filter(BulkImportLog.is_deleted == False).order_by(BulkImportLog.created_at.desc()).limit(100).all()
    return templates.TemplateResponse("bulk_import_history.html", {"request": request, "logs": logs})
