from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple
from datetime import date
import jdatetime

from app.models.customer import Customer
from app.models.project_member import ProjectMember
from app.models.project import Project
from app.models.financial_obligation import FinancialObligation, ObligationType, ObligationStatus
from app.models.financial_credit import FinancialCredit, CreditType, CreditStatus
from app.models.journal_entry import JournalEntry, JournalStatus
from app.models.journal_line import JournalLine, DebitCredit
from app.models.account import Account, AccountType
from app.models.contract import Contract, ContractType, ContractStatus
from app.models.bank_statement import BankStatement, StatementType
from app.schemas.bulk_import import BulkImportCreate, BulkImportRow, BulkImportType, DebitType, CreditType as CreditTypeEnum
from app.services.document_sequence_service import DocumentSequenceService

class BulkImportService:
    @staticmethod
    def validate_members(db: Session, member_numbers: List[str], project_id: int) -> Tuple[List[str], List[str]]:
        """بررسی اعتبار شماره‌های عضو و بازگرداندن لیست معتبر و نامعتبر"""
        valid = []
        invalid = []
        
        for member_no in member_numbers:
            if not member_no or not str(member_no).strip():
                continue
                
            member_no = str(member_no).strip()
            customer = db.query(Customer).filter(
                Customer.customer_no == member_no,
                Customer.is_deleted == False
            ).first()
            
            if not customer:
                invalid.append(f"{member_no} (مشتری وجود ندارد)")
                continue
            
            # بررسی عضویت در پروژه
            project_member = db.query(ProjectMember).filter(
                ProjectMember.customer_id == customer.id,
                ProjectMember.project_id == project_id,
                ProjectMember.is_deleted == False
            ).first()
            
            if not project_member:
                invalid.append(f"{member_no} (عضو پروژه نیست)")
                continue
            
            valid.append({
                "member_no": member_no,
                "customer_id": customer.id,
                "customer": customer,
                "project_member": project_member
            })
        
        return valid, invalid

    @staticmethod
    def process_debit_bulk(db: Session, data: BulkImportCreate) -> Dict[str, Any]:
        """پردازش بدهکار گروهی"""
        # ۱. اعتبارسنجی شماره‌های عضو
        member_numbers = [row.member_no for row in data.rows if row.member_no]
        valid_members, invalid_members = BulkImportService.validate_members(
            db, member_numbers, data.project_id
        )
        
        if invalid_members:
            return {
                "success": False,
                "message": f"{len(invalid_members)} شماره عضو نامعتبر است",
                "errors": invalid_members
            }
        
        # ۲. ایجاد سند حسابداری
        journal_no = DocumentSequenceService.get_next_journal_number(db)
        journal = JournalEntry(
            journal_no=journal_no,
            journal_date=data.document_date,
            status=JournalStatus.POSTED,
            description=data.document_description,
            reference_type="BULK_DEBIT"
        )
        db.add(journal)
        db.flush()
        
        # ۳. برای هر ردیف، FinancialObligation و JournalLine ایجاد کن
        total_amount = 0
        created_count = 0
        
        for row in data.rows:
            if not row.member_no:
                continue
                
            # پیدا کردن مشتری معتبر
            valid_member = next((m for m in valid_members if m["member_no"] == row.member_no), None)
            if not valid_member:
                continue
            
            # ایجاد بدهی
            obligation_no = DocumentSequenceService.get_next_obligation_number(db)
            obligation_type = ObligationType.PROJECT_PLAN
            
            if data.debit_type == "PROJECT_PLAN":
                obligation_type = ObligationType.PROJECT_PLAN
            elif data.debit_type == "UNIT_DIFFERENCE":
                obligation_type = ObligationType.UNIT_DIFFERENCE
            elif data.debit_type == "PENALTY":
                obligation_type = ObligationType.PENALTY
            elif data.debit_type == "SERVICE_FEE":
                obligation_type = ObligationType.SERVICE_FEE
            else:
                obligation_type = ObligationType.OTHER
            
            obligation = FinancialObligation(
                obligation_no=obligation_no,
                customer_id=valid_member["customer_id"],
                project_id=data.project_id,
                obligation_type=obligation_type,
                amount=row.amount or 0,
                paid_amount=0,
                status=ObligationStatus.PENDING,
                description=row.description or data.document_description,
                reference_id=journal_no
            )
            db.add(obligation)
            db.flush()
            
            # ایجاد JournalLine (بدهکار حساب مشتری)
            # پیدا کردن حساب مشتری یا ایجاد آن
            account = db.query(Account).filter(
                Account.account_type == AccountType.MEMBER,
                Account.is_active == True
            ).first()
            
            if not account:
                # ایجاد حساب پیش‌فرض برای مشتریان
                account = Account(
                    account_code="1000",
                    account_name="حساب مشتریان",
                    account_type=AccountType.MEMBER,
                    is_active=True
                )
                db.add(account)
                db.flush()
            
            journal_line = JournalLine(
                journal_id=journal.id,
                account_id=account.id,
                debit_credit=DebitCredit.DEBIT,
                amount=row.amount or 0,
                description=f"بدهی - {row.description or data.document_description}",
                analytic_account_id=None
            )
            db.add(journal_line)
            
            # ایجاد JournalLine (بستانکار حساب پروژه)
            project_account = db.query(Account).filter(
                Account.account_type == AccountType.PROJECT,
                Account.is_active == True
            ).first()
            
            if not project_account:
                project_account = Account(
                    account_code="2000",
                    account_name="حساب پروژه‌ها",
                    account_type=AccountType.PROJECT,
                    is_active=True
                )
                db.add(project_account)
                db.flush()
            
            journal_line_credit = JournalLine(
                journal_id=journal.id,
                account_id=project_account.id,
                debit_credit=DebitCredit.CREDIT,
                amount=row.amount or 0,
                description=f"بدهی - {row.description or data.document_description}",
                analytic_account_id=None
            )
            db.add(journal_line_credit)
            
            total_amount += row.amount or 0
            created_count += 1
        
        # ۴. Commit همه تغییرات
        db.commit()
        
        return {
            "success": True,
            "message": f"{created_count} بدهی با موفقیت ایجاد شد",
            "journal_no": journal_no,
            "total_rows": created_count,
            "total_amount": total_amount,
            "errors": []
        }

    @staticmethod
    def process_credit_bulk(db: Session, data: BulkImportCreate) -> Dict[str, Any]:
        """پردازش بستانکار گروهی (وام، سوبسید، تخفیف، چک)"""
        # ۱. اعتبارسنجی شماره‌های عضو
        member_numbers = [row.member_no for row in data.rows if row.member_no]
        valid_members, invalid_members = BulkImportService.validate_members(
            db, member_numbers, data.project_id
        )
        
        if invalid_members:
            return {
                "success": False,
                "message": f"{len(invalid_members)} شماره عضو نامعتبر است",
                "errors": invalid_members
            }
        
        # ۲. ایجاد سند حسابداری
        journal_no = DocumentSequenceService.get_next_journal_number(db)
        journal = JournalEntry(
            journal_no=journal_no,
            journal_date=data.document_date,
            status=JournalStatus.POSTED,
            description=data.document_description,
            reference_type="BULK_CREDIT"
        )
        db.add(journal)
        db.flush()
        
        # ۳. برای هر ردیف، FinancialCredit و JournalLine ایجاد کن
        total_amount = 0
        created_count = 0
        
        for row in data.rows:
            if not row.member_no:
                continue
                
            valid_member = next((m for m in valid_members if m["member_no"] == row.member_no), None)
            if not valid_member:
                continue
            
            # ایجاد اعتبار
            credit_no = DocumentSequenceService.get_next_credit_number(db)
            credit_type = CreditTypeEnum.LOAN
            
            if data.credit_type == "LOAN":
                credit_type = CreditTypeEnum.LOAN
            elif data.credit_type == "SUBSIDY":
                credit_type = CreditTypeEnum.SUBSIDY
            elif data.credit_type == "DISCOUNT":
                credit_type = CreditTypeEnum.DISCOUNT
            elif data.credit_type == "CHEQUE":
                credit_type = CreditTypeEnum.OTHER
            else:
                credit_type = CreditTypeEnum.OTHER
            
            credit = FinancialCredit(
                credit_no=credit_no,
                customer_id=valid_member["customer_id"],
                project_id=data.project_id,
                credit_type=credit_type,
                amount=row.amount or 0,
                status=CreditStatus.APPROVED,
                credit_date=data.document_date,
                description=row.description or data.document_description,
                reference_id=journal_no
            )
            db.add(credit)
            db.flush()
            
            # ایجاد JournalLine (بدهکار حساب پروژه)
            project_account = db.query(Account).filter(
                Account.account_type == AccountType.PROJECT,
                Account.is_active == True
            ).first()
            
            if not project_account:
                project_account = Account(
                    account_code="2000",
                    account_name="حساب پروژه‌ها",
                    account_type=AccountType.PROJECT,
                    is_active=True
                )
                db.add(project_account)
                db.flush()
            
            journal_line = JournalLine(
                journal_id=journal.id,
                account_id=project_account.id,
                debit_credit=DebitCredit.DEBIT,
                amount=row.amount or 0,
                description=f"اعتبار - {row.description or data.document_description}",
                analytic_account_id=None
            )
            db.add(journal_line)
            
            # ایجاد JournalLine (بستانکار حساب مشتری)
            account = db.query(Account).filter(
                Account.account_type == AccountType.MEMBER,
                Account.is_active == True
            ).first()
            
            if not account:
                account = Account(
                    account_code="1000",
                    account_name="حساب مشتریان",
                    account_type=AccountType.MEMBER,
                    is_active=True
                )
                db.add(account)
                db.flush()
            
            journal_line_credit = JournalLine(
                journal_id=journal.id,
                account_id=account.id,
                debit_credit=DebitCredit.CREDIT,
                amount=row.amount or 0,
                description=f"اعتبار - {row.description or data.document_description}",
                analytic_account_id=None
            )
            db.add(journal_line_credit)
            
            total_amount += row.amount or 0
            created_count += 1
        
        # ۴. Commit همه تغییرات
        db.commit()
        
        return {
            "success": True,
            "message": f"{created_count} اعتبار با موفقیت ایجاد شد",
            "journal_no": journal_no,
            "total_rows": created_count,
            "total_amount": total_amount,
            "errors": []
        }

    @staticmethod
    def process_member_bulk(db: Session, data: BulkImportCreate) -> Dict[str, Any]:
        """پردازش ورود گروهی اعضا"""
        created_count = 0
        errors = []
        
        for row in data.rows:
            if not row.member_no:
                continue
            
            # بررسی وجود مشتری
            customer = db.query(Customer).filter(
                Customer.customer_no == row.member_no,
                Customer.is_deleted == False
            ).first()
            
            if customer:
                errors.append(f"{row.member_no} - قبلاً ثبت شده است")
                continue
            
            # ایجاد مشتری جدید
            customer = Customer(
                customer_no=row.member_no,
                full_name=row.full_name or f"کاربر {row.member_no}",
                national_code=row.national_code if hasattr(row, 'national_code') else None,
                mobile=row.mobile if hasattr(row, 'mobile') else None,
                phone=row.phone if hasattr(row, 'phone') else None,
                address=row.address if hasattr(row, 'address') else None,
                status="ACTIVE"
            )
            db.add(customer)
            db.flush()
            
            # ایجاد عضویت در پروژه
            project_member = ProjectMember(
                customer_id=customer.id,
                project_id=data.project_id,
                join_date=data.document_date,
                status="ACTIVE"
            )
            db.add(project_member)
            
            created_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{created_count} عضو با موفقیت ایجاد شد",
            "total_rows": created_count,
            "errors": errors
        }

    @staticmethod
    def process_bulk_import(db: Session, data: BulkImportCreate) -> Dict[str, Any]:
        """پردازش اصلی ورود گروهی بر اساس نوع"""
        if data.import_type == BulkImportType.DEBIT:
            return BulkImportService.process_debit_bulk(db, data)
        elif data.import_type == BulkImportType.CREDIT:
            return BulkImportService.process_credit_bulk(db, data)
        elif data.import_type == BulkImportType.MEMBER:
            return BulkImportService.process_member_bulk(db, data)
        else:
            return {
                "success": False,
                "message": "نوع عملیات نامعتبر است",
                "errors": ["نوع عملیات پشتیبانی نمی‌شود"]
            }