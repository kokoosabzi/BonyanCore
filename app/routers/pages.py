from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from urllib.parse import urlencode

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.customer_service import CustomerService
from app.services.project_service import ProjectService
from app.services.project_member_service import ProjectMemberService
from app.services.contract_service import ContractService
from app.services.financial_obligation_service import FinancialObligationService
from app.services.bank_service import BankService
from app.services.bank_account_service import BankAccountService
from app.services.unit_service import UnitService
from app.services.receipt_service import ReceiptService
from app.core.templates import create_templates
from app.models.project_member import ProjectMember
from app.models.receipt import Receipt
from app.models.user import User

router = APIRouter(prefix="/pages", tags=["Pages"])
templates = create_templates()

# ============================================================
# صفحه اصلی (داشبورد)
# ============================================================
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = ProjectService.get_all(db)
    customers = CustomerService.get_all(db)
    members = db.query(ProjectMember).filter(ProjectMember.is_deleted == False).all()
    contracts = ContractService.get_all(db)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard",
            "projects_count": len(projects),
            "customers_count": len(customers),
            "members_count": len(members),
            "contracts_count": len(contracts)
        }
    )


# ============================================================
# پروژه‌ها
# ============================================================
# و برای سایر صفحات، active_page را اضافه کن:
# مثلاً برای project_list:
@router.get("/projects", response_class=HTMLResponse)
async def project_list(request: Request, db: Session = Depends(get_db)):
    projects = ProjectService.get_all(db)
    return templates.TemplateResponse(
        "project_list.html",
        {
            "request": request,
            "active_page": "projects",
            "projects": projects,
            "delete_success": request.query_params.get("deleted") == "1",
        }
    )

@router.get("/projects/create", response_class=HTMLResponse)
async def project_create_form(request: Request):
    return templates.TemplateResponse("project_form.html", {"request": request, "project": None})

@router.post("/projects/create")
async def project_create(
    request: Request,
    project_code: str = Form(...),
    name: str = Form(...),
    start_date: str = Form(...),
    status: str = Form("ACTIVE"),
    total_units: int = Form(0),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.schemas.project import ProjectCreate
    data = ProjectCreate(
        project_code=project_code,
        name=name,
        start_date=start_date,
        status=status,
        total_units=total_units,
        description=description
    )
    ProjectService.create(db, data)
    return RedirectResponse("/pages/projects", status_code=303)

# ============================================================
# ویرایش پروژه
# ============================================================
@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def project_edit_form(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="پروژه پیدا نشد")
    return templates.TemplateResponse(
        "project_edit.html",
        {"request": request, "active_page": "projects", "project": project}
    )

@router.post("/projects/{project_id}/edit")
async def project_edit(
    project_id: int,
    name: str = Form(...),
    start_date: str = Form(...),
    status: str = Form("ACTIVE"),
    total_units: int = Form(0),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.schemas.project import ProjectUpdate
    data = ProjectUpdate(
        name=name,
        start_date=start_date,
        status=status,
        total_units=total_units,
        description=description
    )
    ProjectService.update(db, project_id, data)
    return RedirectResponse("/pages/projects", status_code=303)

@router.post("/projects/{project_id}/delete")
async def project_delete(project_id: int, db: Session = Depends(get_db)):
    if not ProjectService.delete(db, project_id):
        raise HTTPException(status_code=404, detail="پروژه پیدا نشد")
    return RedirectResponse("/pages/projects?deleted=1", status_code=303)

# ============================================================
# ویرایش مشتری
# ============================================================
@router.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def customer_edit_form(request: Request, customer_id: int, db: Session = Depends(get_db)):
    customer = CustomerService.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="مشتری پیدا نشد")
    return templates.TemplateResponse(
        "customer_edit.html",
        {"request": request, "active_page": "customers", "customer": customer}
    )

@router.post("/customers/{customer_id}/edit")
async def customer_edit(
    customer_id: int,
    full_name: str = Form(...),
    national_code: str = Form(""),
    birth_date: str = Form(""),
    mobile: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    job: str = Form(""),
    status: str = Form("ACTIVE"),
    db: Session = Depends(get_db)
):
    from app.schemas.customer import CustomerUpdate
    data = CustomerUpdate(
        full_name=full_name,
        national_code=national_code if national_code else None,
        birth_date=birth_date if birth_date else None,
        mobile=mobile if mobile else None,
        phone=phone if phone else None,
        address=address if address else None,
        job=job if job else None,
        status=status
    )
    CustomerService.update(db, customer_id, data)
    return RedirectResponse("/pages/customers", status_code=303)

@router.post("/customers/{customer_id}/delete")
async def customer_delete(customer_id: int, db: Session = Depends(get_db)):
    if not CustomerService.delete(db, customer_id):
        raise HTTPException(status_code=404, detail="مشتری پیدا نشد")
    return RedirectResponse("/pages/customers?deleted=1", status_code=303)

# ============================================================
# ویرایش عضویت
# ============================================================
@router.get("/memberships/{member_id}/edit", response_class=HTMLResponse)
async def membership_edit_form(request: Request, member_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    membership = db.query(ProjectMember).filter(
        ProjectMember.id == member_id,
        ProjectMember.is_deleted == False
    ).options(
        joinedload(ProjectMember.customer),
        joinedload(ProjectMember.project)
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="عضویت پیدا نشد")
    return templates.TemplateResponse(
        "membership_edit.html",
        {"request": request, "active_page": "memberships", "membership": membership}
    )

@router.post("/memberships/{member_id}/edit")
async def membership_edit(
    member_id: int,
    join_date: str = Form(...),
    status: str = Form("ACTIVE"),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.schemas.project_member import ProjectMemberUpdate
    data = ProjectMemberUpdate(
        join_date=join_date,
        status=status,
        notes=notes if notes else None
    )
    ProjectMemberService.update(db, member_id, data)
    return RedirectResponse("/pages/memberships", status_code=303)

@router.post("/memberships/{member_id}/delete")
async def membership_delete(member_id: int, db: Session = Depends(get_db)):
    ProjectMemberService.delete(db, member_id)
    return RedirectResponse("/pages/memberships", status_code=303)

# ============================================================
# واحدها (Units)
# ============================================================
@router.get("/units", response_class=HTMLResponse)
async def unit_list(request: Request, db: Session = Depends(get_db)):
    units = UnitService.get_all(db)
    return templates.TemplateResponse("unit_list.html", {"request": request, "units": units})

@router.get("/units/create", response_class=HTMLResponse)
async def unit_create_form(request: Request, db: Session = Depends(get_db)):
    projects = ProjectService.get_all(db)
    return templates.TemplateResponse(
        "unit_form.html",
        {"request": request, "unit": None, "projects": projects}
    )

@router.post("/units/create")
async def unit_create(
    request: Request,
    project_id: int = Form(...),
    unit_code: str = Form(...),
    building: str = Form(""),
    floor: int = Form(None),
    unit_number: str = Form(""),
    area: float = Form(None),
    price: int = Form(None),
    status: str = Form("AVAILABLE"),
    db: Session = Depends(get_db)
):
    from app.schemas.unit import UnitCreate
    data = UnitCreate(
        project_id=project_id,
        unit_code=unit_code,
        building=building if building else None,
        floor=floor if floor else None,
        unit_number=unit_number if unit_number else None,
        area=area if area else None,
        price=price if price else None,
        status=status
    )
    UnitService.create(db, data)
    return RedirectResponse("/pages/units", status_code=303)
# ============================================================
# مشتریان
# ============================================================
@router.get("/customers", response_class=HTMLResponse)
async def customer_list(request: Request, db: Session = Depends(get_db)):
    customers = CustomerService.get_all(db)
    return templates.TemplateResponse(
        "customer_list.html",
        {
            "request": request,
            "customers": customers,
            "delete_success": request.query_params.get("deleted") == "1",
        },
    )

@router.get("/customers/create", response_class=HTMLResponse)
async def customer_create_form(request: Request):
    return templates.TemplateResponse("customer_form.html", {"request": request, "customer": None})

@router.post("/customers/create")
async def customer_create(
    request: Request,
    customer_no: str = Form(...),
    full_name: str = Form(...),
    national_code: str = Form(""),
    birth_date: str = Form(""),
    mobile: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    job: str = Form(""),
    status: str = Form("ACTIVE"),
    db: Session = Depends(get_db)
):
    from app.schemas.customer import CustomerCreate
    data = CustomerCreate(
        customer_no=customer_no,
        full_name=full_name,
        national_code=national_code if national_code else None,
        birth_date=birth_date if birth_date else None,
        mobile=mobile if mobile else None,
        phone=phone if phone else None,
        address=address if address else None,
        job=job if job else None,
        status=status
    )
    CustomerService.create(db, data)
    return RedirectResponse("/pages/customers", status_code=303)

# ============================================================
# عضویت
# ============================================================
@router.get("/memberships", response_class=HTMLResponse)
async def membership_list(request: Request, db: Session = Depends(get_db)):
    members = db.query(ProjectMember).filter(ProjectMember.is_deleted == False).all()
    return templates.TemplateResponse("membership_list.html", {"request": request, "members": members})

@router.get("/memberships/create", response_class=HTMLResponse)
async def membership_create_form(request: Request, db: Session = Depends(get_db)):
    customers = CustomerService.get_all(db)
    projects = ProjectService.get_all(db)
    return templates.TemplateResponse(
        "membership_form.html",
        {"request": request, "membership": None, "customers": customers, "projects": projects}
    )

@router.post("/memberships/create")
async def membership_create(
    request: Request,
    customer_id: int = Form(...),
    project_id: int = Form(...),
    join_date: str = Form(...),
    status: str = Form("ACTIVE"),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.schemas.project_member import ProjectMemberCreate
    data = ProjectMemberCreate(
        customer_id=customer_id,
        project_id=project_id,
        join_date=join_date,
        status=status,
        notes=notes if notes else None
    )
    ProjectMemberService.create(db, data)
    return RedirectResponse("/pages/memberships", status_code=303)


# ============================================================
# قراردادها
# ============================================================
@router.get("/contracts", response_class=HTMLResponse)
async def contract_list(request: Request, db: Session = Depends(get_db)):
    contracts = ContractService.get_all(db)
    return templates.TemplateResponse("contract_list.html", {"request": request, "contracts": contracts})

@router.get("/contracts/final/create", response_class=HTMLResponse)
async def final_contract_create_form(request: Request, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    members = db.query(ProjectMember).filter(ProjectMember.is_deleted == False).options(
        joinedload(ProjectMember.customer),
        joinedload(ProjectMember.project)
    ).all()
    units = UnitService.get_all(db)
    return templates.TemplateResponse(
        "final_contract_form.html",
        {"request": request, "contract": None, "members": members, "units": units}
    )

@router.get("/contracts/{contract_id}/edit", response_class=HTMLResponse)
async def contract_edit_form(request: Request, contract_id: int, db: Session = Depends(get_db)):
    contract = ContractService.get_by_id(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="قرارداد پیدا نشد")
    return templates.TemplateResponse(
        "contract_form.html",
        {"request": request, "contract": contract},
    )

@router.post("/contracts/{contract_id}/edit")
async def contract_edit(
    contract_id: int,
    status: str = Form("DRAFT"),
    end_date: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    from app.schemas.contract import ContractUpdate

    try:
        data = ContractUpdate(
            status=status,
            end_date=end_date if end_date else None,
            description=description if description else None,
        )
        if not ContractService.update(db, contract_id, data):
            raise HTTPException(status_code=404, detail="قرارداد پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/contracts", status_code=303)

@router.post("/contracts/{contract_id}/delete")
async def contract_delete(contract_id: int, db: Session = Depends(get_db)):
    if not ContractService.delete(db, contract_id):
        raise HTTPException(status_code=404, detail="قرارداد پیدا نشد")
    return RedirectResponse("/pages/contracts", status_code=303)

# ============================================================
# فیش‌ها (Receipts)
# ============================================================
@router.get("/receipts", response_class=HTMLResponse)
async def receipt_list(request: Request, db: Session = Depends(get_db)):
    receipts = ReceiptService.get_all(db)
    return templates.TemplateResponse("receipt_list.html", {"request": request, "receipts": receipts})

@router.get("/receipts/create", response_class=HTMLResponse)
async def receipt_create_form(request: Request, db: Session = Depends(get_db)):
    customers = CustomerService.get_all(db)
    projects = ProjectService.get_all(db)
    bank_accounts = BankAccountService.get_all(db)
    return templates.TemplateResponse(
        "receipt_form.html",
        {"request": request, "receipt": None, "customers": customers, "projects": projects, "bank_accounts": bank_accounts}
    )

@router.post("/receipts/create")
async def receipt_create(
    request: Request,
    customer_id: int = Form(...),
    project_id: int = Form(...),
    amount: int = Form(...),
    receipt_date: str = Form(...),
    payment_method: str = Form(...),
    bank_account_id: Optional[int] = Form(None),
    cheque_no: str = Form(""),
    cheque_due_date: str = Form(""),
    bank_name: str = Form(""),
    bank_branch: str = Form(""),
    drawer_name: str = Form(""),
    payee_name: str = Form(""),
    deposit_document_type: str = Form(""),
    depositor_name: str = Form(""),
    reference_no: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.schemas.receipt import ReceiptCreate
    data = ReceiptCreate(
        customer_id=customer_id,
        project_id=project_id,
        amount=amount,
        receipt_date=receipt_date,
        payment_method=payment_method,
        bank_account_id=bank_account_id if bank_account_id else None,
        cheque_no=cheque_no if cheque_no else None,
        cheque_due_date=cheque_due_date if cheque_due_date else None,
        bank_name=bank_name if bank_name else None,
        bank_branch=bank_branch if bank_branch else None,
        drawer_name=drawer_name if drawer_name else None,
        payee_name=payee_name if payee_name else None,
        deposit_document_type=(
            deposit_document_type if deposit_document_type else None
        ),
        depositor_name=depositor_name if depositor_name else None,
        reference_no=reference_no if reference_no else None,
        description=description if description else None
    )
    ReceiptService.create(db, data, operator_id=current_user.id)
    return RedirectResponse("/pages/receipts", status_code=303)

@router.get("/receipts/{receipt_id}/edit", response_class=HTMLResponse)
async def receipt_edit_form(request: Request, receipt_id: int, db: Session = Depends(get_db)):
    receipt = ReceiptService.get_by_id(db, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="فیش پیدا نشد")
    return templates.TemplateResponse(
        "receipt_form.html",
        {
            "request": request,
            "receipt": receipt,
            "customers": CustomerService.get_all(db),
            "projects": ProjectService.get_all(db),
            "bank_accounts": BankAccountService.get_all(db),
        },
    )

@router.post("/receipts/{receipt_id}/edit")
async def receipt_edit(
    receipt_id: int,
    amount: int = Form(...),
    receipt_date: str = Form(...),
    payment_method: str = Form(...),
    bank_account_id: Optional[int] = Form(None),
    cheque_no: str = Form(""),
    cheque_due_date: str = Form(""),
    bank_name: str = Form(""),
    bank_branch: str = Form(""),
    drawer_name: str = Form(""),
    payee_name: str = Form(""),
    deposit_document_type: str = Form(""),
    depositor_name: str = Form(""),
    reference_no: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    from app.schemas.receipt import ReceiptUpdate

    try:
        data = ReceiptUpdate(
            amount=amount,
            receipt_date=receipt_date,
            payment_method=payment_method,
            bank_account_id=bank_account_id,
            cheque_no=cheque_no if cheque_no else None,
            cheque_due_date=cheque_due_date if cheque_due_date else None,
            bank_name=bank_name if bank_name else None,
            bank_branch=bank_branch if bank_branch else None,
            drawer_name=drawer_name if drawer_name else None,
            payee_name=payee_name if payee_name else None,
            deposit_document_type=(
                deposit_document_type if deposit_document_type else None
            ),
            depositor_name=depositor_name if depositor_name else None,
            reference_no=reference_no if reference_no else None,
            description=description if description else None,
        )
        if not ReceiptService.update(db, receipt_id, data):
            raise HTTPException(status_code=404, detail="فیش پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/receipts", status_code=303)

@router.post("/receipts/{receipt_id}/delete")
async def receipt_delete(receipt_id: int, db: Session = Depends(get_db)):
    try:
        if not ReceiptService.delete(db, receipt_id):
            raise HTTPException(status_code=404, detail="فیش پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/receipts", status_code=303)


@router.post("/receipts/{receipt_id}/confirm")
async def receipt_confirm(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if not ReceiptService.confirm(
            db,
            receipt_id,
            confirmed_by=current_user.id,
            username=current_user.username,
        ):
            raise HTTPException(status_code=404, detail="فیش پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/receipts", status_code=303)

# ============================================================
# بدهی‌ها (Obligations)
# ============================================================
@router.get("/obligations", response_class=HTMLResponse)
async def obligation_list(request: Request, db: Session = Depends(get_db)):
    obligations = FinancialObligationService.get_all(db)
    return templates.TemplateResponse("obligation_list.html", {"request": request, "obligations": obligations})

@router.get("/obligations/create", response_class=HTMLResponse)
async def obligation_create_form(request: Request, db: Session = Depends(get_db)):
    customers = CustomerService.get_all(db)
    projects = ProjectService.get_all(db)
    return templates.TemplateResponse(
        "obligation_form.html",
        {"request": request, "obligation": None, "customers": customers, "projects": projects}
    )

@router.post("/obligations/create")
async def obligation_create(
    request: Request,
    customer_id: int = Form(...),
    project_id: int = Form(...),
    obligation_type: str = Form(...),
    amount: int = Form(...),
    due_date: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.schemas.financial_obligation import FinancialObligationCreate
    data = FinancialObligationCreate(
        customer_id=customer_id,
        project_id=project_id,
        obligation_type=obligation_type,
        amount=amount,
        due_date=due_date if due_date else None,
        description=description if description else None
    )
    FinancialObligationService.create(
        db,
        data,
        posted_by=current_user.username,
    )
    return RedirectResponse("/pages/obligations", status_code=303)

@router.get("/obligations/{obligation_id}/edit", response_class=HTMLResponse)
async def obligation_edit_form(request: Request, obligation_id: int, db: Session = Depends(get_db)):
    obligation = FinancialObligationService.get_by_id(db, obligation_id)
    if not obligation:
        raise HTTPException(status_code=404, detail="بدهی پیدا نشد")
    return templates.TemplateResponse(
        "obligation_form.html",
        {
            "request": request,
            "obligation": obligation,
            "customers": CustomerService.get_all(db),
            "projects": ProjectService.get_all(db),
        },
    )

@router.post("/obligations/{obligation_id}/edit")
async def obligation_edit(
    obligation_id: int,
    due_date: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    from app.schemas.financial_obligation import FinancialObligationUpdate

    try:
        data = FinancialObligationUpdate(
            due_date=due_date if due_date else None,
            description=description if description else None,
        )
        if not FinancialObligationService.update(db, obligation_id, data):
            raise HTTPException(status_code=404, detail="بدهی پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/obligations", status_code=303)

@router.post("/obligations/{obligation_id}/delete")
async def obligation_delete(obligation_id: int, db: Session = Depends(get_db)):
    try:
        if not FinancialObligationService.delete(db, obligation_id):
            raise HTTPException(status_code=404, detail="بدهی پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/obligations", status_code=303)

# ============================================================
# بانک‌ها
# ============================================================
@router.get("/banks", response_class=HTMLResponse)
async def bank_list(request: Request, db: Session = Depends(get_db)):
    banks = BankService.get_all(db)
    return templates.TemplateResponse("bank_list.html", {"request": request, "banks": banks})

@router.get("/banks/create", response_class=HTMLResponse)
async def bank_create_form(request: Request):
    return templates.TemplateResponse("bank_form.html", {"request": request, "bank": None})

@router.post("/banks/create")
async def bank_create(
    request: Request,
    bank_name: str = Form(...),
    bank_code: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.schemas.bank import BankCreate
    data = BankCreate(
        bank_name=bank_name,
        bank_code=bank_code if bank_code else None,
        description=description if description else None
    )
    BankService.create(db, data)
    return RedirectResponse("/pages/banks", status_code=303)
# ============================================================
# حساب‌های بانکی
# ============================================================
@router.get("/bank-accounts", response_class=HTMLResponse)
async def bank_account_list(request: Request, db: Session = Depends(get_db)):
    accounts = BankAccountService.get_all(db)
    return templates.TemplateResponse("bank_account_list.html", {"request": request, "accounts": accounts})

@router.get("/bank-accounts/create", response_class=HTMLResponse)
async def bank_account_create_form(request: Request, db: Session = Depends(get_db)):
    banks = BankService.get_all(db)
    return templates.TemplateResponse(
        "bank_account_form.html",
        {"request": request, "bank_account": None, "banks": banks}
    )

@router.post("/bank-accounts/create")
async def bank_account_create(
    request: Request,
    bank_id: int = Form(...),
    account_no: str = Form(...),
    sheba: str = Form(""),
    card_no: str = Form(""),
    branch: str = Form(""),
    account_name: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.schemas.bank_account import BankAccountCreate
    data = BankAccountCreate(
        bank_id=bank_id,
        account_no=account_no,
        sheba=sheba if sheba else None,
        card_no=card_no if card_no else None,
        branch=branch if branch else None,
        account_name=account_name if account_name else None,
        description=description if description else None
    )
    BankAccountService.create(db, data)
    return RedirectResponse("/pages/bank-accounts", status_code=303)

@router.get("/transfers", response_class=HTMLResponse)
async def transfer_create_form(
    request: Request,
    created: bool = Query(False),
    db: Session = Depends(get_db),
):
    return templates.TemplateResponse(
        "transfer_form.html",
        {
            "request": request,
            "active_page": "transfers",
            "bank_accounts": BankAccountService.get_all(db),
            "created": created,
        },
    )

@router.get("/units/{unit_id}/edit", response_class=HTMLResponse)
async def unit_edit_form(request: Request, unit_id: int, db: Session = Depends(get_db)):
    unit = UnitService.get_by_id(db, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="واحد پیدا نشد")
    return templates.TemplateResponse(
        "unit_form.html",
        {
            "request": request,
            "unit": unit,
            "projects": ProjectService.get_all(db),
        },
    )

@router.post("/units/{unit_id}/edit")
async def unit_edit(
    unit_id: int,
    unit_code: str = Form(...),
    building: str = Form(""),
    floor: Optional[int] = Form(None),
    unit_number: str = Form(...),
    area: Optional[float] = Form(None),
    price: Optional[int] = Form(None),
    status: str = Form("AVAILABLE"),
    db: Session = Depends(get_db),
):
    from app.schemas.unit import UnitUpdate

    try:
        data = UnitUpdate(
            unit_code=unit_code,
            building=building if building else None,
            floor=floor,
            unit_number=unit_number,
            area=area,
            price=price,
            status=status,
        )
        if not UnitService.update(db, unit_id, data):
            raise HTTPException(status_code=404, detail="واحد پیدا نشد")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse("/pages/units", status_code=303)

@router.post("/units/{unit_id}/delete")
async def unit_delete(unit_id: int, db: Session = Depends(get_db)):
    if not UnitService.delete(db, unit_id):
        raise HTTPException(status_code=404, detail="واحد پیدا نشد")
    return RedirectResponse("/pages/units", status_code=303)
