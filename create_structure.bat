@echo off
chcp 65001 >nul
echo ============================================================
echo Bonyan Core - Full File Generator
echo Creating all 61 files with complete code...
echo ============================================================

REM ============================================
REM ایجاد پوشه‌ها
REM ============================================
echo.
echo [1/5] Creating folders...
mkdir app 2>nul
mkdir app\core 2>nul
mkdir app\models 2>nul
mkdir app\schemas 2>nul
mkdir app\services 2>nul
mkdir app\routers 2>nul
mkdir app\templates 2>nul
mkdir app\static 2>nul
mkdir app\utils 2>nul
mkdir migrations 2>nul
mkdir migrations\versions 2>nul
mkdir docs 2>nul
mkdir imports 2>nul
mkdir exports 2>nul
mkdir uploads 2>nul
mkdir tests 2>nul

REM ============================================
REM فایل‌های __init__.py
REM ============================================
echo.
echo [2/5] Creating __init__.py files...
echo # Empty file > app\__init__.py
echo # Empty file > app\core\__init__.py
echo # Empty file > app\utils\__init__.py
echo # Empty file > tests\__init__.py
echo # Empty file > app\templates\__init__.py
echo # Empty file > app\static\__init__.py

REM ============================================
REM فایل‌های اصلی (Root)
REM ============================================
echo.
echo [3/5] Creating root files...

REM ===== main.py =====
(
echo from fastapi import FastAPI
echo from app.core.config import settings
echo from app.routers import (
echo     customer_router,
echo     project_router,
echo     project_member_router,
echo     contract_router,
echo     financial_obligation_router,
echo     financial_credit_router
echo )
echo from app.core.database import Base, engine
echo.
echo Base.metadata.create_all(bind=engine^)
echo.
echo app = FastAPI(
echo     title=settings.APP_NAME,
echo     version=settings.APP_VERSION,
echo )
echo.
echo app.include_router(customer_router^)
echo app.include_router(project_router^)
echo app.include_router(project_member_router^)
echo app.include_router(contract_router^)
echo app.include_router(financial_obligation_router^)
echo app.include_router(financial_credit_router^)
echo.
echo @app.get("/")
echo async def root(^):
echo     return {
echo         "message": "Bonyan Core API",
echo         "version": settings.APP_VERSION,
echo         "status": "running"
echo     }
echo.
echo @app.get("/health")
echo async def health_check(^):
echo     return {"status": "healthy"}
) > main.py

REM ===== .env =====
(
echo DATABASE_URL=postgresql://bonyan:bonyan123@localhost:5432/bonyan_core
echo SECRET_KEY=your-secret-key-change-in-production
echo APP_NAME=Bonyan Core
echo APP_VERSION=0.1.0
echo DEBUG=True
) > .env

REM ===== requirements.txt =====
(
echo fastapi==0.111.0
echo uvicorn[standard]==0.30.1
echo sqlalchemy==2.0.31
echo alembic==1.13.1
echo psycopg2-binary==2.9.9
echo python-dotenv==1.0.1
echo pydantic==2.7.4
echo pydantic-settings==2.3.4
echo python-multipart==0.0.9
echo openpyxl==3.1.5
echo pandas==2.2.2
echo jinja2==3.1.4
echo weasyprint==62.3
echo jdatetime==6.0.1
) > requirements.txt

REM ===== alembic.ini =====
(
echo [alembic]
echo script_location = migrations
echo prepend_sys_path = .
echo version_path_separator = os
echo sqlalchemy.url = postgresql://bonyan:bonyan123@localhost:5432/bonyan_core
echo.
echo [loggers]
echo keys = root,sqlalchemy,alembic
echo.
echo [handlers]
echo keys = console
echo.
echo [formatters]
echo keys = generic
echo.
echo [logger_root]
echo level = WARN
echo handlers = console
echo qualname =
echo.
echo [logger_sqlalchemy]
echo level = WARN
echo handlers =
echo qualname = sqlalchemy.engine
echo.
echo [logger_alembic]
echo level = INFO
echo handlers =
echo qualname = alembic
echo.
echo [handler_console]
echo class = StreamHandler
echo args = (sys.stderr,^)
echo level = NOTSET
echo formatter = generic
echo.
echo [formatter_generic]
echo format = %%(levelname)-5.5s [%%(name)s] %%(message)s
echo datefmt = %%%%H:%%%%M:%%%%S
) > alembic.ini

REM ===== test_db.py =====
(
echo from app.core.database import engine
echo from sqlalchemy import text
echo.
echo try:
echo     with engine.connect(^) as conn:
echo         result = conn.execute(text("SELECT 1"^)^)
echo         print("✅ Database connection successful!"^)
echo except Exception as e:
echo     print(f"❌ Database connection failed: {e}"^)
) > test_db.py

REM ===== .gitignore =====
(
echo venv/
echo __pycache__/
echo *.pyc
echo .env
echo *.log
echo .vscode/
echo .idea/
echo migrations/versions/*.py
echo !migrations/versions/__init__.py
echo *.db
echo *.sqlite
echo *.sqlite3
) > .gitignore

REM ============================================
REM فایل‌های CORE
REM ============================================
echo.
echo [4/5] Creating core files...

REM ===== app/core/config.py =====
(
echo from pydantic_settings import BaseSettings
echo.
echo class Settings(BaseSettings^):
echo     DATABASE_URL: str = "postgresql://bonyan:bonyan123@localhost:5432/bonyan_core"
echo     SECRET_KEY: str = "your-secret-key-change-in-production"
echo     APP_NAME: str = "Bonyan Core"
echo     APP_VERSION: str = "0.1.0"
echo     DEBUG: bool = True
echo.
echo     class Config:
echo         env_file = ".env"
echo.
echo settings = Settings(^)
) > app\core\config.py

REM ===== app/core/database.py =====
(
echo from sqlalchemy import create_engine
echo from sqlalchemy.orm import sessionmaker, declarative_base
echo from app.core.config import settings
echo.
echo engine = create_engine(settings.DATABASE_URL, echo=True^)
echo SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine^)
echo Base = declarative_base(^)
echo.
echo def get_db(^):
echo     db = SessionLocal(^)
echo     try:
echo         yield db
echo     finally:
echo         db.close(^)
) > app\core\database.py

REM ============================================
REM فایل‌های MODELS
REM ============================================
echo.
echo [5/5] Creating models...

REM ===== app/models/base.py =====
(
echo from sqlalchemy import Column, BigInteger, DateTime, Boolean, String
echo from sqlalchemy.sql import func
echo from app.core.database import Base
echo.
echo class BaseModel(Base^):
echo     __abstract__ = True
echo.
echo     id = Column(BigInteger, primary_key=True, index=True^)
echo     created_at = Column(DateTime, server_default=func.now(^), nullable=False^)
echo     updated_at = Column(DateTime, server_default=func.now(^), onupdate=func.now(^)^)
echo     deleted_at = Column(DateTime, nullable=True^)
echo     is_deleted = Column(Boolean, default=False^)
echo     created_by = Column(String(50^), nullable=True^)
echo     updated_by = Column(String(50^), nullable=True^)
echo     deleted_by = Column(String(50^), nullable=True^)
) > app\models\base.py

REM ===== app/models/__init__.py =====
(
echo from app.models.base import BaseModel
echo from app.models.company import Company
echo from app.models.project import Project
echo from app.models.customer import Customer
echo from app.models.project_member import ProjectMember
echo from app.models.unit import Unit
echo from app.models.contract import Contract, ContractType, ContractStatus
echo from app.models.financial_obligation import FinancialObligation, ObligationType, ObligationStatus
echo from app.models.financial_credit import FinancialCredit, CreditType, CreditStatus
echo from app.models.account import Account, AccountType
echo from app.models.bank import Bank
echo from app.models.bank_account import BankAccount
echo from app.models.journal_entry import JournalEntry, JournalStatus
echo from app.models.journal_line import JournalLine, DebitCredit
echo from app.models.analytic_account import AnalyticAccount
echo from app.models.audit_log import AuditLog
echo from app.models.document_sequence import DocumentSequence
echo from app.models.receipt import Receipt, PaymentMethod, ReceiptStatus
echo from app.models.payment import Payment, PaymentStatus
echo from app.models.transfer import Transfer, TransferStatus
echo from app.models.user import User
echo from app.models.role import Role
echo from app.models.permission import Permission
) > app\models\__init__.py

REM ===== app/models/company.py =====
(
echo from sqlalchemy import Column, String, Boolean
echo from app.models.base import BaseModel
echo.
echo class Company(BaseModel^):
echo     __tablename__ = "companies"
echo.
echo     name = Column(String(200^), nullable=False^)
echo     registration_no = Column(String(50^), nullable=True^)
echo     tax_id = Column(String(50^), nullable=True^)
echo     address = Column(String(500^), nullable=True^)
echo     phone = Column(String(20^), nullable=True^)
echo     email = Column(String(100^), nullable=True^)
echo     is_active = Column(Boolean, default=True^)
) > app\models\company.py

REM ===== app/models/project.py =====
(
echo from sqlalchemy import Column, String, Date, Boolean, Text, Integer
echo from app.models.base import BaseModel
echo.
echo class Project(BaseModel^):
echo     __tablename__ = "projects"
echo.
echo     project_code = Column(String(2^), nullable=False, unique=True, index=True^)
echo     name = Column(String(200^), nullable=False^)
echo     start_date = Column(Date, nullable=False^)
echo     status = Column(String(20^), default="ACTIVE"^)
echo     total_units = Column(Integer, default=0^)
echo     description = Column(Text, nullable=True^)
echo     is_active = Column(Boolean, default=True^)
) > app\models\project.py

REM ===== app/models/customer.py =====
(
echo from sqlalchemy import Column, String, Date, Boolean, Text, BigInteger
echo from sqlalchemy.orm import relationship
echo from app.models.base import BaseModel
echo.
echo class Customer(BaseModel^):
echo     __tablename__ = "customers"
echo.
echo     customer_no = Column(String(6^), nullable=False, unique=True, index=True^)
echo     full_name = Column(String(200^), nullable=False^)
echo     national_code = Column(String(10^), unique=True, nullable=True^)
echo     birth_date = Column(Date, nullable=True^)
echo     mobile = Column(String(11^), nullable=True^)
echo     phone = Column(String(20^), nullable=True^)
echo     address = Column(Text, nullable=True^)
echo     job = Column(String(100^), nullable=True^)
echo     status = Column(String(20^), default="ACTIVE"^)
echo     dynamic_data = Column(Text, nullable=True^)
echo.
echo     project_members = relationship("ProjectMember", back_populates="customer"^)
) > app\models\customer.py

REM ===== app/models/project_member.py =====
(
echo from sqlalchemy import Column, String, Date, Boolean, BigInteger, ForeignKey
echo from sqlalchemy.orm import relationship
echo from app.models.base import BaseModel
echo.
echo class ProjectMember(BaseModel^):
echo     __tablename__ = "project_members"
echo.
echo     customer_id = Column(BigInteger, ForeignKey("customers.id"^), nullable=False^)
echo     project_id = Column(BigInteger, ForeignKey("projects.id"^), nullable=False^)
echo     join_date = Column(Date, nullable=False^)
echo     status = Column(String(20^), default="ACTIVE"^)
echo     notes = Column(String(500^), nullable=True^)
echo.
echo     customer = relationship("Customer", back_populates="project_members"^)
echo     project = relationship("Project"^)
echo     contracts = relationship("Contract", back_populates="project_member"^)
) > app\models\project_member.py

REM ===== app/models/unit.py =====
(
echo from sqlalchemy import Column, String, Integer, Float, Boolean, BigInteger, ForeignKey
echo from app.models.base import BaseModel
echo.
echo class Unit(BaseModel^):
echo     __tablename__ = "units"
echo.
echo     unit_code = Column(String(20^), nullable=False, unique=True, index=True^)
echo     project_id = Column(BigInteger, ForeignKey("projects.id"^), nullable=False^)
echo     building = Column(String(10^), nullable=True^)
echo     floor = Column(Integer, nullable=True^)
echo     unit_number = Column(String(10^), nullable=False^)
echo     area = Column(Float, nullable=True^)
echo     price = Column(BigInteger, nullable=True^)
echo     status = Column(String(20^), default="AVAILABLE"^)
echo     is_active = Column(Boolean, default=True^)
) > app\models\unit.py

REM ===== app/models/contract.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
echo from sqlalchemy.orm import relationship
echo from app.models.base import BaseModel
echo import enum
echo.
echo class ContractType(str, enum.Enum^):
echo     MEMBERSHIP = "MEMBERSHIP"
echo     FINAL_UNIT = "FINAL_UNIT"
echo.
echo class ContractStatus(str, enum.Enum^):
echo     DRAFT = "DRAFT"
echo     ACTIVE = "ACTIVE"
echo     COMPLETED = "COMPLETED"
echo     CANCELLED = "CANCELLED"
echo.
echo class Contract(BaseModel^):
echo     __tablename__ = "contracts"
echo.
echo     contract_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     project_member_id = Column(BigInteger, ForeignKey("project_members.id"^), nullable=False^)
echo     contract_type = Column(Enum(ContractType^), nullable=False^)
echo     status = Column(Enum(ContractStatus^), default=ContractStatus.DRAFT^)
echo     start_date = Column(Date, nullable=False^)
echo     end_date = Column(Date, nullable=True^)
echo     unit_id = Column(BigInteger, ForeignKey("units.id"^), nullable=True^)
echo     final_price = Column(BigInteger, nullable=True^)
echo     description = Column(Text, nullable=True^)
echo     signed_by = Column(String(200^), nullable=True^)
echo     signed_date = Column(Date, nullable=True^)
echo.
echo     project_member = relationship("ProjectMember", back_populates="contracts"^)
echo     unit = relationship("Unit"^)
) > app\models\contract.py

REM ===== app/models/financial_obligation.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
echo from app.models.base import BaseModel
echo import enum
echo.
echo class ObligationType(str, enum.Enum^):
echo     PROJECT_PLAN = "PROJECT_PLAN"
echo     UNIT_DIFFERENCE = "UNIT_DIFFERENCE"
echo     PENALTY = "PENALTY"
echo     INCREASE_ADJUSTMENT = "INCREASE_ADJUSTMENT"
echo     SERVICE_FEE = "SERVICE_FEE"
echo     OTHER = "OTHER"
echo.
echo class ObligationStatus(str, enum.Enum^):
echo     PENDING = "PENDING"
echo     PARTIAL = "PARTIAL"
echo     PAID = "PAID"
echo     CANCELLED = "CANCELLED"
echo.
echo class FinancialObligation(BaseModel^):
echo     __tablename__ = "financial_obligations"
echo.
echo     obligation_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     customer_id = Column(BigInteger, ForeignKey("customers.id"^), nullable=False^)
echo     project_id = Column(BigInteger, ForeignKey("projects.id"^), nullable=False^)
echo     contract_id = Column(BigInteger, ForeignKey("contracts.id"^), nullable=True^)
echo     obligation_type = Column(Enum(ObligationType^), nullable=False^)
echo     amount = Column(BigInteger, nullable=False^)
echo     paid_amount = Column(BigInteger, default=0^)
echo     status = Column(Enum(ObligationStatus^), default=ObligationStatus.PENDING^)
echo     due_date = Column(Date, nullable=True^)
echo     description = Column(Text, nullable=True^)
echo     reference_id = Column(String(100^), nullable=True^)
) > app\models\financial_obligation.py

REM ===== app/models/financial_credit.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
echo from app.models.base import BaseModel
echo import enum
echo.
echo class CreditType(str, enum.Enum^):
echo     PAYMENT = "PAYMENT"
echo     LOAN = "LOAN"
echo     SUBSIDY = "SUBSIDY"
echo     DISCOUNT = "DISCOUNT"
echo     DECREASE_ADJUSTMENT = "DECREASE_ADJUSTMENT"
echo     OTHER = "OTHER"
echo.
echo class CreditStatus(str, enum.Enum^):
echo     PENDING = "PENDING"
echo     APPROVED = "APPROVED"
echo     REVERSED = "REVERSED"
echo.
echo class FinancialCredit(BaseModel^):
echo     __tablename__ = "financial_credits"
echo.
echo     credit_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     customer_id = Column(BigInteger, ForeignKey("customers.id"^), nullable=False^)
echo     project_id = Column(BigInteger, ForeignKey("projects.id"^), nullable=False^)
echo     contract_id = Column(BigInteger, ForeignKey("contracts.id"^), nullable=True^)
echo     credit_type = Column(Enum(CreditType^), nullable=False^)
echo     amount = Column(BigInteger, nullable=False^)
echo     status = Column(Enum(CreditStatus^), default=CreditStatus.PENDING^)
echo     credit_date = Column(Date, nullable=False^)
echo     description = Column(Text, nullable=True^)
echo     reference_id = Column(String(100^), nullable=True^)
echo     bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"^), nullable=True^)
echo     cheque_no = Column(String(50^), nullable=True^)
) > app\models\financial_credit.py

REM ===== app/models/account.py =====
(
echo from sqlalchemy import Column, String, Boolean, BigInteger, Text, Enum, ForeignKey
echo from app.models.base import BaseModel
echo import enum
echo.
echo class AccountType(str, enum.Enum^):
echo     BANK = "BANK"
echo     CASH = "CASH"
echo     TREASURY = "TREASURY"
echo     MEMBER = "MEMBER"
echo     PROJECT = "PROJECT"
echo     SUSPENSE = "SUSPENSE"
echo.
echo class Account(BaseModel^):
echo     __tablename__ = "accounts"
echo.
echo     account_code = Column(String(20^), nullable=False, unique=True, index=True^)
echo     account_name = Column(String(200^), nullable=False^)
echo     account_type = Column(Enum(AccountType^), nullable=False^)
echo     parent_id = Column(BigInteger, ForeignKey("accounts.id"^), nullable=True^)
echo     is_active = Column(Boolean, default=True^)
echo     description = Column(Text, nullable=True^)
) > app\models\account.py

REM ===== app/models/bank.py =====
(
echo from sqlalchemy import Column, String, Boolean, Text
echo from app.models.base import BaseModel
echo.
echo class Bank(BaseModel^):
echo     __tablename__ = "banks"
echo.
echo     bank_name = Column(String(100^), nullable=False^)
echo     bank_code = Column(String(10^), nullable=True^)
echo     is_active = Column(Boolean, default=True^)
echo     description = Column(Text, nullable=True^)
) > app\models\bank.py

REM ===== app/models/bank_account.py =====
(
echo from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, Text
echo from app.models.base import BaseModel
echo.
echo class BankAccount(BaseModel^):
echo     __tablename__ = "bank_accounts"
echo.
echo     bank_id = Column(BigInteger, ForeignKey("banks.id"^), nullable=False^)
echo     account_no = Column(String(30^), nullable=False^)
echo     sheba = Column(String(30^), nullable=True^)
echo     card_no = Column(String(20^), nullable=True^)
echo     branch = Column(String(100^), nullable=True^)
echo     account_name = Column(String(200^), nullable=True^)
echo     currency = Column(String(3^), default="IRR"^)
echo     is_active = Column(Boolean, default=True^)
echo     description = Column(Text, nullable=True^)
) > app\models\bank_account.py

REM ===== app/models/journal_entry.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum, DateTime
echo from sqlalchemy.orm import relationship
echo from app.models.base import BaseModel
echo import enum
echo.
echo class JournalStatus(str, enum.Enum^):
echo     DRAFT = "DRAFT"
echo     POSTED = "POSTED"
echo     CANCELLED = "CANCELLED"
echo.
echo class JournalEntry(BaseModel^):
echo     __tablename__ = "journal_entries"
echo.
echo     journal_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     journal_date = Column(Date, nullable=False^)
echo     status = Column(Enum(JournalStatus^), default=JournalStatus.DRAFT^)
echo     description = Column(Text, nullable=True^)
echo     posted_by = Column(String(50^), nullable=True^)
echo     posted_at = Column(DateTime, nullable=True^)
echo     reference_type = Column(String(50^), nullable=True^)
echo     reference_id = Column(BigInteger, nullable=True^)
echo.
echo     lines = relationship("JournalLine", back_populates="journal"^)
) > app\models\journal_entry.py

REM ===== app/models/journal_line.py =====
(
echo from sqlalchemy import Column, String, BigInteger, ForeignKey, Text, Enum
echo from sqlalchemy.orm import relationship
echo from app.models.base import BaseModel
echo import enum
echo.
echo class DebitCredit(str, enum.Enum^):
echo     DEBIT = "DEBIT"
echo     CREDIT = "CREDIT"
echo.
echo class JournalLine(BaseModel^):
echo     __tablename__ = "journal_lines"
echo.
echo     journal_id = Column(BigInteger, ForeignKey("journal_entries.id"^), nullable=False^)
echo     account_id = Column(BigInteger, ForeignKey("accounts.id"^), nullable=False^)
echo     debit_credit = Column(Enum(DebitCredit^), nullable=False^)
echo     amount = Column(BigInteger, nullable=False^)
echo     description = Column(Text, nullable=True^)
echo     analytic_account_id = Column(BigInteger, ForeignKey("analytic_accounts.id"^), nullable=True^)
echo.
echo     journal = relationship("JournalEntry", back_populates="lines"^)
echo     account = relationship("Account"^)
echo     analytic_account = relationship("AnalyticAccount"^)
) > app\models\journal_line.py

REM ===== app/models/analytic_account.py =====
(
echo from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, Text
echo from app.models.base import BaseModel
echo.
echo class AnalyticAccount(BaseModel^):
echo     __tablename__ = "analytic_accounts"
echo.
echo     code = Column(String(20^), nullable=False, unique=True, index=True^)
echo     name = Column(String(200^), nullable=False^)
echo     parent_id = Column(BigInteger, ForeignKey("analytic_accounts.id"^), nullable=True^)
echo     is_active = Column(Boolean, default=True^)
echo     description = Column(Text, nullable=True^)
echo     reference_type = Column(String(50^), nullable=True^)
echo     reference_id = Column(BigInteger, nullable=True^)
) > app\models\analytic_account.py

REM ===== app/models/audit_log.py =====
(
echo from sqlalchemy import Column, String, DateTime, BigInteger, Text, JSON
echo from sqlalchemy.sql import func
echo from app.core.database import Base
echo.
echo class AuditLog(Base^):
echo     __tablename__ = "audit_logs"
echo.
echo     id = Column(BigInteger, primary_key=True, index=True^)
echo     user_id = Column(BigInteger, nullable=True^)
echo     username = Column(String(50^), nullable=True^)
echo     ip_address = Column(String(45^), nullable=True^)
echo     table_name = Column(String(50^), nullable=False^)
echo     record_id = Column(BigInteger, nullable=False^)
echo     operation = Column(String(20^), nullable=False^)
echo     old_values = Column(JSON, nullable=True^)
echo     new_values = Column(JSON, nullable=True^)
echo     created_at = Column(DateTime, server_default=func.now(^), nullable=False^)
echo     module = Column(String(50^), nullable=True^)
) > app\models\audit_log.py

REM ===== app/models/document_sequence.py =====
(
echo from sqlalchemy import Column, String, Integer, BigInteger
echo from app.models.base import BaseModel
echo.
echo class DocumentSequence(BaseModel^):
echo     __tablename__ = "document_sequences"
echo.
echo     prefix = Column(String(10^), nullable=False, unique=True, index=True^)
echo     year = Column(String(2^), nullable=False^)
echo     current_number = Column(Integer, default=0^)
echo     description = Column(String(200^), nullable=True^)
echo.
echo     def get_next_number(self^) -> str:
echo         self.current_number += 1
echo         return f"{self.prefix}-{self.year}-{self.current_number:06d}"
) > app\models\document_sequence.py

REM ===== app/models/receipt.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
echo from app.models.base import BaseModel
echo import enum
echo.
echo class PaymentMethod(str, enum.Enum^):
echo     CASH = "CASH"
echo     CHEQUE = "CHEQUE"
echo     TRANSFER = "TRANSFER"
echo     POS = "POS"
echo     OTHER = "OTHER"
echo.
echo class ReceiptStatus(str, enum.Enum^):
echo     DRAFT = "DRAFT"
echo     CONFIRMED = "CONFIRMED"
echo     CANCELLED = "CANCELLED"
echo.
echo class Receipt(BaseModel^):
echo     __tablename__ = "receipts"
echo.
echo     receipt_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     customer_id = Column(BigInteger, ForeignKey("customers.id"^), nullable=False^)
echo     project_id = Column(BigInteger, ForeignKey("projects.id"^), nullable=False^)
echo     contract_id = Column(BigInteger, ForeignKey("contracts.id"^), nullable=True^)
echo     amount = Column(BigInteger, nullable=False^)
echo     receipt_date = Column(Date, nullable=False^)
echo     payment_method = Column(Enum(PaymentMethod^), nullable=False^)
echo     bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"^), nullable=True^)
echo     cheque_no = Column(String(50^), nullable=True^)
echo     cheque_due_date = Column(Date, nullable=True^)
echo     description = Column(Text, nullable=True^)
echo     status = Column(Enum(ReceiptStatus^), default=ReceiptStatus.DRAFT^)
echo     operator_id = Column(BigInteger, ForeignKey("users.id"^), nullable=True^)
echo     confirmed_by = Column(BigInteger, ForeignKey("users.id"^), nullable=True^)
echo     confirmed_at = Column(Date, nullable=True^)
echo     journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"^), nullable=True^)
) > app\models\receipt.py

REM ===== app/models/payment.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
echo from app.models.base import BaseModel
echo import enum
echo.
echo class PaymentStatus(str, enum.Enum^):
echo     DRAFT = "DRAFT"
echo     CONFIRMED = "CONFIRMED"
echo     CANCELLED = "CANCELLED"
echo.
echo class Payment(BaseModel^):
echo     __tablename__ = "payments"
echo.
echo     payment_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     project_id = Column(BigInteger, ForeignKey("projects.id"^), nullable=False^)
echo     payee_name = Column(String(200^), nullable=False^)
echo     amount = Column(BigInteger, nullable=False^)
echo     payment_date = Column(Date, nullable=False^)
echo     bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"^), nullable=True^)
echo     cheque_no = Column(String(50^), nullable=True^)
echo     description = Column(Text, nullable=True^)
echo     status = Column(Enum(PaymentStatus^), default=PaymentStatus.DRAFT^)
echo     operator_id = Column(BigInteger, ForeignKey("users.id"^), nullable=True^)
echo     confirmed_by = Column(BigInteger, ForeignKey("users.id"^), nullable=True^)
echo     confirmed_at = Column(Date, nullable=True^)
echo     journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"^), nullable=True^)
echo     category = Column(String(50^), nullable=True^)
) > app\models\payment.py

REM ===== app/models/transfer.py =====
(
echo from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
echo from app.models.base import BaseModel
echo import enum
echo.
echo class TransferStatus(str, enum.Enum^):
echo     DRAFT = "DRAFT"
echo     CONFIRMED = "CONFIRMED"
echo     CANCELLED = "CANCELLED"
echo.
echo class Transfer(BaseModel^):
echo     __tablename__ = "transfers"
echo.
echo     transfer_no = Column(String(50^), nullable=False, unique=True, index=True^)
echo     from_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"^), nullable=False^)
echo     to_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"^), nullable=False^)
echo     amount = Column(BigInteger, nullable=False^)
echo     transfer_date = Column(Date, nullable=False^)
echo     description = Column(Text, nullable=True^)
echo     status = Column(Enum(TransferStatus^), default=TransferStatus.DRAFT^)
echo     operator_id = Column(BigInteger, ForeignKey("users.id"^), nullable=True^)
echo     confirmed_by = Column(BigInteger, ForeignKey("users.id"^), nullable=True^)
echo     confirmed_at = Column(Date, nullable=True^)
echo     journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"^), nullable=True^)
) > app\models\transfer.py

REM ===== app/models/user.py =====
(
echo from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, DateTime, Text
echo from app.models.base import BaseModel
echo.
echo class User(BaseModel^):
echo     __tablename__ = "users"
echo.
echo     username = Column(String(50^), nullable=False, unique=True, index=True^)
echo     email = Column(String(100^), nullable=True, unique=True^)
echo     full_name = Column(String(200^), nullable=False^)
echo     hashed_password = Column(String(200^), nullable=False^)
echo     is_active = Column(Boolean, default=True^)
echo     is_superuser = Column(Boolean, default=False^)
echo     last_login = Column(DateTime, nullable=True^)
echo     phone = Column(String(20^), nullable=True^)
echo     role_id = Column(BigInteger, ForeignKey("roles.id"^), nullable=True^)
) > app\models\user.py

REM ===== app/models/role.py =====
(
echo from sqlalchemy import Column, String, Boolean, Text
echo from app.models.base import BaseModel
echo.
echo class Role(BaseModel^):
echo     __tablename__ = "roles"
echo.
echo     name = Column(String(50^), nullable=False, unique=True, index=True^)
echo     description = Column(Text, nullable=True^)
echo     is_active = Column(Boolean, default=True^)
echo     permissions = Column(Text, nullable=True^)
) > app\models\role.py

REM ===== app/models/permission.py =====
(
echo from sqlalchemy import Column, String, Boolean, Text
echo from app.models.base import BaseModel
echo.
echo class Permission(BaseModel^):
echo     __tablename__ = "permissions"
echo.
echo     name = Column(String(100^), nullable=False, unique=True, index=True^)
echo     code = Column(String(50^), nullable=False, unique=True, index=True^)
echo     module = Column(String(50^), nullable=False^)
echo     description = Column(Text, nullable=True^)
echo     is_active = Column(Boolean, default=True^)
) > app\models\permission.py

REM ============================================
REM فایل‌های SCHEMAS
REM ============================================
echo.
echo Creating schemas...

REM ===== app/schemas/__init__.py =====
(
echo from app.schemas.customer import CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse
echo from app.schemas.project import ProjectBase, ProjectCreate, ProjectUpdate, ProjectResponse
echo from app.schemas.project_member import ProjectMemberBase, ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
echo from app.schemas.contract import ContractBase, ContractCreate, ContractUpdate, ContractResponse, ContractType, ContractStatus
echo from app.schemas.financial_obligation import FinancialObligationBase, FinancialObligationCreate, FinancialObligationUpdate, FinancialObligationResponse, ObligationType, ObligationStatus
echo from app.schemas.financial_credit import FinancialCreditBase, FinancialCreditCreate, FinancialCreditUpdate, FinancialCreditResponse, CreditType, CreditStatus
) > app\schemas\__init__.py

REM ===== app/schemas/customer.py =====
(
echo from pydantic import BaseModel, Field, field_validator
echo from typing import Optional
echo from datetime import date, datetime
echo.
echo class CustomerBase(BaseModel^):
echo     customer_no: str = Field(...^, min_length=6, max_length=6, description="شماره مشتری ۶ رقمی"^)
echo     full_name: str = Field(...^, max_length=200^)
echo     national_code: Optional[str] = Field(None, max_length=10^)
echo     birth_date: Optional[date] = None
echo     mobile: Optional[str] = Field(None, max_length=11^)
echo     phone: Optional[str] = Field(None, max_length=20^)
echo     address: Optional[str] = None
echo     job: Optional[str] = Field(None, max_length=100^)
echo     status: Optional[str] = "ACTIVE"
echo     dynamic_data: Optional[str] = None
echo.
echo     @field_validator('customer_no'^)
echo     @classmethod
echo     def validate_customer_no(cls, v: str^) -> str:
echo         if not v.isdigit(^):
echo             raise ValueError('شماره مشتری باید فقط شامل اعداد باشد'^)
echo         return v
echo.
echo     @field_validator('national_code'^)
echo     @classmethod
echo     def validate_national_code(cls, v: Optional[str]^) -> Optional[str]:
echo         if v and not v.isdigit(^):
echo             raise ValueError('کد ملی باید فقط شامل اعداد باشد'^)
echo         return v
echo.
echo class CustomerCreate(CustomerBase^):
echo     pass
echo.
echo class CustomerUpdate(BaseModel^):
echo     full_name: Optional[str] = Field(None, max_length=200^)
echo     national_code: Optional[str] = Field(None, max_length=10^)
echo     birth_date: Optional[date] = None
echo     mobile: Optional[str] = Field(None, max_length=11^)
echo     phone: Optional[str] = Field(None, max_length=20^)
echo     address: Optional[str] = None
echo     job: Optional[str] = Field(None, max_length=100^)
echo     status: Optional[str] = None
echo     dynamic_data: Optional[str] = None
echo.
echo class CustomerResponse(CustomerBase^):
echo     id: int
echo     created_at: datetime
echo     updated_at: datetime
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\customer.py

REM ===== app/schemas/project.py =====
(
echo from pydantic import BaseModel, Field, field_validator
echo from typing import Optional
echo from datetime import date, datetime
echo.
echo class ProjectBase(BaseModel^):
echo     project_code: str = Field(...^, min_length=2, max_length=2, description="کد پروژه ۲ رقمی"^)
echo     name: str = Field(...^, max_length=200^)
echo     start_date: date
echo     status: Optional[str] = "ACTIVE"
echo     total_units: Optional[int] = 0
echo     description: Optional[str] = None
echo.
echo     @field_validator('project_code'^)
echo     @classmethod
echo     def validate_project_code(cls, v: str^) -> str:
echo         if not v.isdigit(^):
echo             raise ValueError('کد پروژه باید فقط شامل اعداد باشد'^)
echo         return v
echo.
echo class ProjectCreate(ProjectBase^):
echo     pass
echo.
echo class ProjectUpdate(BaseModel^):
echo     name: Optional[str] = Field(None, max_length=200^)
echo     start_date: Optional[date] = None
echo     status: Optional[str] = None
echo     total_units: Optional[int] = None
echo     description: Optional[str] = None
echo.
echo class ProjectResponse(ProjectBase^):
echo     id: int
echo     created_at: datetime
echo     updated_at: datetime
echo     is_active: bool
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\project.py

REM ===== app/schemas/project_member.py =====
(
echo from pydantic import BaseModel, Field
echo from typing import Optional
echo from datetime import date, datetime
echo.
echo class ProjectMemberBase(BaseModel^):
echo     customer_id: int = Field(...^, description="شناسه مشتری"^)
echo     project_id: int = Field(...^, description="شناسه پروژه"^)
echo     join_date: date = Field(...^, description="تاریخ عضویت"^)
echo     status: Optional[str] = "ACTIVE"
echo     notes: Optional[str] = Field(None, max_length=500^)
echo.
echo class ProjectMemberCreate(ProjectMemberBase^):
echo     pass
echo.
echo class ProjectMemberUpdate(BaseModel^):
echo     join_date: Optional[date] = None
echo     status: Optional[str] = None
echo     notes: Optional[str] = Field(None, max_length=500^)
echo.
echo class ProjectMemberResponse(ProjectMemberBase^):
echo     id: int
echo     created_at: datetime
echo     updated_at: datetime
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\project_member.py

REM ===== app/schemas/contract.py =====
(
echo from pydantic import BaseModel, Field
echo from typing import Optional
echo from datetime import date, datetime
echo from enum import Enum
echo.
echo class ContractType(str, Enum^):
echo     MEMBERSHIP = "MEMBERSHIP"
echo     FINAL_UNIT = "FINAL_UNIT"
echo.
echo class ContractStatus(str, Enum^):
echo     DRAFT = "DRAFT"
echo     ACTIVE = "ACTIVE"
echo     COMPLETED = "COMPLETED"
echo     CANCELLED = "CANCELLED"
echo.
echo class ContractBase(BaseModel^):
echo     project_member_id: int
echo     contract_type: ContractType
echo     status: Optional[ContractStatus] = ContractStatus.DRAFT
echo     start_date: date
echo     end_date: Optional[date] = None
echo     unit_id: Optional[int] = None
echo     final_price: Optional[int] = None
echo     description: Optional[str] = None
echo     signed_by: Optional[str] = None
echo     signed_date: Optional[date] = None
echo.
echo class ContractCreate(ContractBase^):
echo     pass
echo.
echo class ContractUpdate(BaseModel^):
echo     status: Optional[ContractStatus] = None
echo     end_date: Optional[date] = None
echo     unit_id: Optional[int] = None
echo     final_price: Optional[int] = None
echo     description: Optional[str] = None
echo     signed_by: Optional[str] = None
echo     signed_date: Optional[date] = None
echo.
echo class ContractResponse(ContractBase^):
echo     id: int
echo     contract_no: str
echo     created_at: datetime
echo     updated_at: datetime
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\contract.py

REM ===== app/schemas/financial_obligation.py =====
(
echo from pydantic import BaseModel, Field
echo from typing import Optional
echo from datetime import date, datetime
echo from enum import Enum
echo.
echo class ObligationType(str, Enum^):
echo     PROJECT_PLAN = "PROJECT_PLAN"
echo     UNIT_DIFFERENCE = "UNIT_DIFFERENCE"
echo     PENALTY = "PENALTY"
echo     INCREASE_ADJUSTMENT = "INCREASE_ADJUSTMENT"
echo     SERVICE_FEE = "SERVICE_FEE"
echo     OTHER = "OTHER"
echo.
echo class ObligationStatus(str, Enum^):
echo     PENDING = "PENDING"
echo     PARTIAL = "PARTIAL"
echo     PAID = "PAID"
echo     CANCELLED = "CANCELLED"
echo.
echo class FinancialObligationBase(BaseModel^):
echo     customer_id: int
echo     project_id: int
echo     contract_id: Optional[int] = None
echo     obligation_type: ObligationType
echo     amount: int = Field(...^, gt=0, description="مبلغ بدهی"^)
echo     paid_amount: Optional[int] = 0
echo     status: Optional[ObligationStatus] = ObligationStatus.PENDING
echo     due_date: Optional[date] = None
echo     description: Optional[str] = None
echo     reference_id: Optional[str] = None
echo.
echo class FinancialObligationCreate(FinancialObligationBase^):
echo     pass
echo.
echo class FinancialObligationUpdate(BaseModel^):
echo     paid_amount: Optional[int] = None
echo     status: Optional[ObligationStatus] = None
echo     due_date: Optional[date] = None
echo     description: Optional[str] = None
echo.
echo class FinancialObligationResponse(FinancialObligationBase^):
echo     id: int
echo     obligation_no: str
echo     created_at: datetime
echo     updated_at: datetime
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\financial_obligation.py

REM ===== app/schemas/financial_credit.py =====
(
echo from pydantic import BaseModel, Field
echo from typing import Optional
echo from datetime import date, datetime
echo from enum import Enum
echo.
echo class CreditType(str, Enum^):
echo     PAYMENT = "PAYMENT"
echo     LOAN = "LOAN"
echo     SUBSIDY = "SUBSIDY"
echo     DISCOUNT = "DISCOUNT"
echo     DECREASE_ADJUSTMENT = "DECREASE_ADJUSTMENT"
echo     OTHER = "OTHER"
echo.
echo class CreditStatus(str, Enum^):
echo     PENDING = "PENDING"
echo     APPROVED = "APPROVED"
echo     REVERSED = "REVERSED"
echo.
echo class FinancialCreditBase(BaseModel^):
echo     customer_id: int
echo     project_id: int
echo     contract_id: Optional[int] = None
echo     credit_type: CreditType
echo     amount: int = Field(...^, gt=0, description="مبلغ اعتبار"^)
echo     status: Optional[CreditStatus] = CreditStatus.PENDING
echo     credit_date: date
echo     description: Optional[str] = None
echo     reference_id: Optional[str] = None
echo     bank_account_id: Optional[int] = None
echo     cheque_no: Optional[str] = Field(None, max_length=50^)
echo.
echo class FinancialCreditCreate(FinancialCreditBase^):
echo     pass
echo.
echo class FinancialCreditUpdate(BaseModel^):
echo     amount: Optional[int] = None
echo     status: Optional[CreditStatus] = None
echo     description: Optional[str] = None
echo     bank_account_id: Optional[int] = None
echo     cheque_no: Optional[str] = Field(None, max_length=50^)
echo.
echo class FinancialCreditResponse(FinancialCreditBase^):
echo     id: int
echo     credit_no: str
echo     created_at: datetime
echo     updated_at: datetime
echo.
echo     class Config:
echo         from_attributes = True
) > app\schemas\financial_credit.py

REM ============================================
REM فایل‌های SERVICES
REM ============================================
echo.
echo Creating services...

REM ===== app/services/__init__.py =====
(
echo from app.services.customer_service import CustomerService
echo from app.services.project_service import ProjectService
echo from app.services.project_member_service import ProjectMemberService
echo from app.services.contract_service import ContractService
echo from app.services.financial_obligation_service import FinancialObligationService
echo from app.services.financial_credit_service import FinancialCreditService
echo from app.services.document_sequence_service import DocumentSequenceService
) > app\services\__init__.py

REM ===== app/services/customer_service.py =====
(
echo from sqlalchemy.orm import Session
echo from sqlalchemy import or_
echo from app.models.customer import Customer
echo from app.schemas.customer import CustomerCreate, CustomerUpdate
echo.
echo class CustomerService:
echo     @staticmethod
echo     def create(db: Session, data: CustomerCreate^) -> Customer:
echo         customer = Customer(**data.model_dump(^)^)
echo         db.add(customer^)
echo         db.commit(^)
echo         db.refresh(customer^)
echo         return customer
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, customer_id: int^) -> Customer ^| None:
echo         return db.query(Customer^).filter(Customer.id == customer_id, Customer.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_customer_no(db: Session, customer_no: str^) -> Customer ^| None:
echo         return db.query(Customer^).filter(Customer.customer_no == customer_no, Customer.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_all(db: Session, skip: int = 0, limit: int = 100, search: str = None^):
echo         query = db.query(Customer^).filter(Customer.is_deleted == False^)
echo         if search:
echo             query = query.filter(or_(Customer.full_name.ilike(f"%%{search}%%"^), Customer.customer_no.ilike(f"%%{search}%%"^), Customer.national_code.ilike(f"%%{search}%%"^), Customer.mobile.ilike(f"%%{search}%%"^)^)^)
echo         return query.offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, customer_id: int, data: CustomerUpdate^) -> Customer ^| None:
echo         customer = CustomerService.get_by_id(db, customer_id^)
echo         if not customer:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(customer, key, value^)
echo         db.commit(^)
echo         db.refresh(customer^)
echo         return customer
echo.
echo     @staticmethod
echo     def delete(db: Session, customer_id: int^) -> bool:
echo         customer = CustomerService.get_by_id(db, customer_id^)
echo         if not customer:
echo             return False
echo         customer.is_deleted = True
echo         db.commit(^)
echo         return True
) > app\services\customer_service.py

REM ===== app/services/project_service.py =====
(
echo from sqlalchemy.orm import Session
echo from sqlalchemy import or_
echo from app.models.project import Project
echo from app.schemas.project import ProjectCreate, ProjectUpdate
echo.
echo class ProjectService:
echo     @staticmethod
echo     def create(db: Session, data: ProjectCreate^) -> Project:
echo         project = Project(**data.model_dump(^)^)
echo         db.add(project^)
echo         db.commit(^)
echo         db.refresh(project^)
echo         return project
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, project_id: int^) -> Project ^| None:
echo         return db.query(Project^).filter(Project.id == project_id, Project.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_code(db: Session, project_code: str^) -> Project ^| None:
echo         return db.query(Project^).filter(Project.project_code == project_code, Project.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_all(db: Session, skip: int = 0, limit: int = 100, search: str = None^):
echo         query = db.query(Project^).filter(Project.is_deleted == False^)
echo         if search:
echo             query = query.filter(or_(Project.name.ilike(f"%%{search}%%"^), Project.project_code.ilike(f"%%{search}%%"^)^)^)
echo         return query.offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, project_id: int, data: ProjectUpdate^) -> Project ^| None:
echo         project = ProjectService.get_by_id(db, project_id^)
echo         if not project:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(project, key, value^)
echo         db.commit(^)
echo         db.refresh(project^)
echo         return project
echo.
echo     @staticmethod
echo     def delete(db: Session, project_id: int^) -> bool:
echo         project = ProjectService.get_by_id(db, project_id^)
echo         if not project:
echo             return False
echo         project.is_deleted = True
echo         db.commit(^)
echo         return True
) > app\services\project_service.py

REM ===== app/services/project_member_service.py =====
(
echo from sqlalchemy.orm import Session
echo from app.models.project_member import ProjectMember
echo from app.schemas.project_member import ProjectMemberCreate, ProjectMemberUpdate
echo.
echo class ProjectMemberService:
echo     @staticmethod
echo     def create(db: Session, data: ProjectMemberCreate^) -> ProjectMember:
echo         existing = db.query(ProjectMember^).filter(ProjectMember.customer_id == data.customer_id, ProjectMember.project_id == data.project_id, ProjectMember.is_deleted == False^).first(^)
echo         if existing:
echo             raise ValueError("این مشتری قبلاً در این پروژه عضو شده است"^)
echo         member = ProjectMember(**data.model_dump(^)^)
echo         db.add(member^)
echo         db.commit(^)
echo         db.refresh(member^)
echo         return member
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, member_id: int^) -> ProjectMember ^| None:
echo         return db.query(ProjectMember^).filter(ProjectMember.id == member_id, ProjectMember.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_customer_project(db: Session, customer_id: int, project_id: int^) -> ProjectMember ^| None:
echo         return db.query(ProjectMember^).filter(ProjectMember.customer_id == customer_id, ProjectMember.project_id == project_id, ProjectMember.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100^):
echo         return db.query(ProjectMember^).filter(ProjectMember.project_id == project_id, ProjectMember.is_deleted == False^).offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def get_by_customer(db: Session, customer_id: int^):
echo         return db.query(ProjectMember^).filter(ProjectMember.customer_id == customer_id, ProjectMember.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, member_id: int, data: ProjectMemberUpdate^) -> ProjectMember ^| None:
echo         member = ProjectMemberService.get_by_id(db, member_id^)
echo         if not member:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(member, key, value^)
echo         db.commit(^)
echo         db.refresh(member^)
echo         return member
echo.
echo     @staticmethod
echo     def delete(db: Session, member_id: int^) -> bool:
echo         member = ProjectMemberService.get_by_id(db, member_id^)
echo         if not member:
echo             return False
echo         member.is_deleted = True
echo         db.commit(^)
echo         return True
) > app\services\project_member_service.py

REM ===== app/services/contract_service.py =====
(
echo from sqlalchemy.orm import Session
echo from app.models.contract import Contract, ContractType
echo from app.schemas.contract import ContractCreate, ContractUpdate
echo from app.services.document_sequence_service import DocumentSequenceService
echo.
echo class ContractService:
echo     @staticmethod
echo     def create(db: Session, data: ContractCreate^) -> Contract:
echo         contract_no = DocumentSequenceService.get_next_contract_number(db^)
echo         contract = Contract(contract_no=contract_no, **data.model_dump(^)^)
echo         db.add(contract^)
echo         db.commit(^)
echo         db.refresh(contract^)
echo         return contract
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, contract_id: int^) -> Contract ^| None:
echo         return db.query(Contract^).filter(Contract.id == contract_id, Contract.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_all(db: Session, project_member_id: int = None, contract_type: ContractType = None, skip: int = 0, limit: int = 100^):
echo         query = db.query(Contract^).filter(Contract.is_deleted == False^)
echo         if project_member_id:
echo             query = query.filter(Contract.project_member_id == project_member_id^)
echo         if contract_type:
echo             query = query.filter(Contract.contract_type == contract_type^)
echo         return query.offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, contract_id: int, data: ContractUpdate^) -> Contract ^| None:
echo         contract = ContractService.get_by_id(db, contract_id^)
echo         if not contract:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(contract, key, value^)
echo         db.commit(^)
echo         db.refresh(contract^)
echo         return contract
echo.
echo     @staticmethod
echo     def delete(db: Session, contract_id: int^) -> bool:
echo         contract = ContractService.get_by_id(db, contract_id^)
echo         if not contract:
echo             return False
echo         contract.is_deleted = True
echo         db.commit(^)
echo         return True
) > app\services\contract_service.py

REM ===== app/services/financial_obligation_service.py =====
(
echo from sqlalchemy.orm import Session
echo from app.models.financial_obligation import FinancialObligation, ObligationType, ObligationStatus
echo from app.schemas.financial_obligation import FinancialObligationCreate, FinancialObligationUpdate
echo from app.services.document_sequence_service import DocumentSequenceService
echo.
echo class FinancialObligationService:
echo     @staticmethod
echo     def create(db: Session, data: FinancialObligationCreate^) -> FinancialObligation:
echo         obligation_no = DocumentSequenceService.get_next_obligation_number(db^)
echo         obligation = FinancialObligation(obligation_no=obligation_no, **data.model_dump(^)^)
echo         db.add(obligation^)
echo         db.commit(^)
echo         db.refresh(obligation^)
echo         return obligation
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, obligation_id: int^) -> FinancialObligation ^| None:
echo         return db.query(FinancialObligation^).filter(FinancialObligation.id == obligation_id, FinancialObligation.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_customer(db: Session, customer_id: int^):
echo         return db.query(FinancialObligation^).filter(FinancialObligation.customer_id == customer_id, FinancialObligation.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def get_by_project(db: Session, project_id: int^):
echo         return db.query(FinancialObligation^).filter(FinancialObligation.project_id == project_id, FinancialObligation.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100^):
echo         query = db.query(FinancialObligation^).filter(FinancialObligation.is_deleted == False^)
echo         if customer_id:
echo             query = query.filter(FinancialObligation.customer_id == customer_id^)
echo         if project_id:
echo             query = query.filter(FinancialObligation.project_id == project_id^)
echo         return query.offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, obligation_id: int, data: FinancialObligationUpdate^) -> FinancialObligation ^| None:
echo         obligation = FinancialObligationService.get_by_id(db, obligation_id^)
echo         if not obligation:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(obligation, key, value^)
echo         db.commit(^)
echo         db.refresh(obligation^)
echo         return obligation
echo.
echo     @staticmethod
echo     def delete(db: Session, obligation_id: int^) -> bool:
echo         obligation = FinancialObligationService.get_by_id(db, obligation_id^)
echo         if not obligation:
echo             return False
echo         obligation.is_deleted = True
echo         db.commit(^)
echo         return True
echo.
echo     @staticmethod
echo     def get_total_obligations(db: Session, customer_id: int^) -> int:
echo         total = db.query(FinancialObligation^).filter(FinancialObligation.customer_id == customer_id, FinancialObligation.is_deleted == False, FinancialObligation.status != ObligationStatus.CANCELLED^).with_entities(FinancialObligation.amount^).all(^)
echo         return sum([t[0] for t in total]^) if total else 0
) > app\services\financial_obligation_service.py

REM ===== app/services/financial_credit_service.py =====
(
echo from sqlalchemy.orm import Session
echo from app.models.financial_credit import FinancialCredit, CreditType, CreditStatus
echo from app.schemas.financial_credit import FinancialCreditCreate, FinancialCreditUpdate
echo from app.services.document_sequence_service import DocumentSequenceService
echo.
echo class FinancialCreditService:
echo     @staticmethod
echo     def create(db: Session, data: FinancialCreditCreate^) -> FinancialCredit:
echo         credit_no = DocumentSequenceService.get_next_credit_number(db^)
echo         credit = FinancialCredit(credit_no=credit_no, **data.model_dump(^)^)
echo         db.add(credit^)
echo         db.commit(^)
echo         db.refresh(credit^)
echo         return credit
echo.
echo     @staticmethod
echo     def get_by_id(db: Session, credit_id: int^) -> FinancialCredit ^| None:
echo         return db.query(FinancialCredit^).filter(FinancialCredit.id == credit_id, FinancialCredit.is_deleted == False^).first(^)
echo.
echo     @staticmethod
echo     def get_by_customer(db: Session, customer_id: int^):
echo         return db.query(FinancialCredit^).filter(FinancialCredit.customer_id == customer_id, FinancialCredit.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def get_by_project(db: Session, project_id: int^):
echo         return db.query(FinancialCredit^).filter(FinancialCredit.project_id == project_id, FinancialCredit.is_deleted == False^).all(^)
echo.
echo     @staticmethod
echo     def get_all(db: Session, customer_id: int = None, project_id: int = None, skip: int = 0, limit: int = 100^):
echo         query = db.query(FinancialCredit^).filter(FinancialCredit.is_deleted == False^)
echo         if customer_id:
echo             query = query.filter(FinancialCredit.customer_id == customer_id^)
echo         if project_id:
echo             query = query.filter(FinancialCredit.project_id == project_id^)
echo         return query.offset(skip^).limit(limit^).all(^)
echo.
echo     @staticmethod
echo     def update(db: Session, credit_id: int, data: FinancialCreditUpdate^) -> FinancialCredit ^| None:
echo         credit = FinancialCreditService.get_by_id(db, credit_id^)
echo         if not credit:
echo             return None
echo         for key, value in data.model_dump(exclude_unset=True^).items(^):
echo             setattr(credit, key, value^)
echo         db.commit(^)
echo         db.refresh(credit^)
echo         return credit
echo.
echo     @staticmethod
echo     def delete(db: Session, credit_id: int^) -> bool:
echo         credit = FinancialCreditService.get_by_id(db, credit_id^)
echo         if not credit:
echo             return False
echo         credit.is_deleted = True
echo         db.commit(^)
echo         return True
echo.
echo     @staticmethod
echo     def get_total_credits(db: Session, customer_id: int^) -> int:
echo         total = db.query(FinancialCredit^).filter(FinancialCredit.customer_id == customer_id, FinancialCredit.is_deleted == False, FinancialCredit.status != CreditStatus.REVERSED^).with_entities(FinancialCredit.amount^).all(^)
echo         return sum([t[0] for t in total]^) if total else 0
echo.
echo     @staticmethod
echo     def get_net_balance(db: Session, customer_id: int^) -> int:
echo         from app.services.financial_obligation_service import FinancialObligationService
echo         total_obligations = FinancialObligationService.get_total_obligations(db, customer_id^)
echo         total_credits = FinancialCreditService.get_total_credits(db, customer_id^)
echo         return total_obligations - total_credits
) > app\services\financial_credit_service.py

REM ===== app/services/document_sequence_service.py =====
(
echo from sqlalchemy.orm import Session
echo from app.models.document_sequence import DocumentSequence
echo import jdatetime
echo.
echo class DocumentSequenceService:
echo     @staticmethod
echo     def get_next_number(db: Session, prefix: str^) -> str:
echo         now = jdatetime.datetime.now(^)
echo         year = str(now.year %% 100^).zfill(2^)
echo         sequence = db.query(DocumentSequence^).filter(DocumentSequence.prefix == prefix, DocumentSequence.year == year^).first(^)
echo         if not sequence:
echo             sequence = DocumentSequence(prefix=prefix, year=year, current_number=0^)
echo             db.add(sequence^)
echo             db.commit(^)
echo             db.refresh(sequence^)
echo         sequence.current_number += 1
echo         db.commit(^)
echo         db.refresh(sequence^)
echo         return f"{prefix}-{year}-{sequence.current_number:06d}"
echo.
echo     @staticmethod
echo     def get_next_contract_number(db: Session^) -> str:
echo         return DocumentSequenceService.get_next_number(db, "CTR"^)
echo.
echo     @staticmethod
echo     def get_next_obligation_number(db: Session^) -> str:
echo         return DocumentSequenceService.get_next_number(db, "OBL"^)
echo.
echo     @staticmethod
echo     def get_next_credit_number(db: Session^) -> str:
echo         return DocumentSequenceService.get_next_number(db, "CRD"^)
echo.
echo     @staticmethod
echo     def get_next_receipt_number(db: Session^) -> str:
echo         return DocumentSequenceService.get_next_number(db, "RCV"^)
echo.
echo     @staticmethod
echo     def get_next_payment_number(db: Session^) -> str:
echo         return DocumentSequenceService.get_next_number(db, "PAY"^)
echo.
echo     @staticmethod
echo     def get_next_journal_number(db: Session^) -> str:
echo         return DocumentSequenceService.get_next_number(db, "JV"^)
) > app\services\document_sequence_service.py

REM ============================================
REM فایل‌های ROUTERS
REM ============================================
echo.
echo Creating routers...

REM ===== app/routers/__init__.py =====
(
echo from app.routers.customer import router as customer_router
echo from app.routers.project import router as project_router
echo from app.routers.project_member import router as project_member_router
echo from app.routers.contract import router as contract_router
echo from app.routers.financial_obligation import router as financial_obligation_router
echo from app.routers.financial_credit import router as financial_credit_router
) > app\routers\__init__.py

REM ===== app/routers/customer.py =====
(
echo from fastapi import APIRouter, Depends, HTTPException, Query, status
echo from sqlalchemy.orm import Session
echo from typing import Optional, List
echo from app.core.database import get_db
echo from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
echo from app.services.customer_service import CustomerService
echo.
echo router = APIRouter(prefix="/api/v1/customers", tags=["Customers"]^)
echo.
echo @router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED^)
echo def create_customer(data: CustomerCreate, db: Session = Depends(get_db^)^):
echo     existing = CustomerService.get_by_customer_no(db, data.customer_no^)
echo     if existing:
echo         raise HTTPException(status_code=400, detail="شماره مشتری قبلاً ثبت شده است"^)
echo     return CustomerService.create(db, data^)
echo.
echo @router.get("/", response_model=List[CustomerResponse]^)
echo def get_customers(skip: int = Query(0, ge=0^), limit: int = Query(100, ge=1, le=1000^), search: Optional[str] = None, db: Session = Depends(get_db^)^):
echo     return CustomerService.get_all(db, skip, limit, search^)
echo.
echo @router.get("/{customer_id}", response_model=CustomerResponse^)
echo def get_customer(customer_id: int, db: Session = Depends(get_db^)^):
echo     customer = CustomerService.get_by_id(db, customer_id^)
echo     if not customer:
echo         raise HTTPException(status_code=404, detail="مشتری پیدا نشد"^)
echo     return customer
echo.
echo @router.put("/{customer_id}", response_model=CustomerResponse^)
echo def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db^)^):
echo     customer = CustomerService.update(db, customer_id, data^)
echo     if not customer:
echo         raise HTTPException(status_code=404, detail="مشتری پیدا نشد"^)
echo     return customer
echo.
echo @router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT^)
echo def delete_customer(customer_id: int, db: Session = Depends(get_db^)^):
echo     if not CustomerService.delete(db, customer_id^):
echo         raise HTTPException(status_code=404, detail="مشتری پیدا نشد"^)
) > app\routers\customer.py

REM ===== app/routers/project.py =====
(
echo from fastapi import APIRouter, Depends, HTTPException, Query, status
echo