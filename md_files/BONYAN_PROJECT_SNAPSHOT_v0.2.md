# Bonyan Project Snapshot v0.2

## هدف

سامانه سبک مدیریت تعاونی‌های ساختمانی و حسابداری پروژه‌های مسکونی.

هدف نسخه اول:

- مدیریت پروژه
- مدیریت اعضا
- قرارداد عضویت و قرارداد نهایی واحد
- مدیریت بدهی و آورده اعضا
- ثبت دریافت و پرداخت
- مدیریت بانک و حساب‌ها
- حسابداری دوبل ساده
- گزارش‌گیری
- قابلیت توسعه اطلاعات توسط کاربر


---

# اصول توسعه

سه اصل اصلی:

1. سریع
2. سبک
3. قابل توسعه


از طراحی بیش از حد پیچیده جلوگیری شود.


---

# تکنولوژی

Backend:

Python + FastAPI


Database:

PostgreSQL


ORM:

SQLAlchemy


Migration:

Alembic


Frontend:

Jinja2 + Bootstrap + Javascript


Reports:

Excel / PDF


---

# معماری

نوع:

Modular Monolith


نه:

- Microservice
- Plugin Based
- Event Driven


ساختار:

app/

 core/

 models/

 schemas/

 services/

 routers/

 templates/

 static/


---

# مدل داده


## Customer

کلید داخلی:

id


شماره مشتری:

customer_no

یکتا و غیرقابل تغییر


---

## Dynamic Fields

سیستم Hybrid است.


اطلاعات هسته ثابت هستند.

اطلاعات توصیفی Dynamic هستند.


Dynamic مجاز:

- آدرس
- شغل
- توضیحات
- اطلاعات تکمیلی


Dynamic غیرمجاز:

- مبلغ
- حساب
- بدهی
- سند مالی


---

# پروژه


Project

دارای:

- کد دو رقمی
- نام
- وضعیت


---

# عضویت


ProjectMember


ارتباط:

Customer

با

Project


---

# واحد


Unit


شامل:

- کد واحد
- بلوک
- طبقه
- متراژ


---

# قرارداد


دو نوع قرارداد:


1- Membership Contract

قرارداد عضویت پروژه


2- Final Unit Contract

قرارداد نهایی واحد


---

# مدل مالی


## Account

تمام حساب‌ها در این جدول هستند.


انواع:

BANK

CASH

TREASURY

MEMBER

PROJECT

SUSPENSE



---

# FinancialTransaction


مرکز تمام عملیات مالی:


انواع:

- بدهی پلن پروژه
- پرداخت عضو
- وام
- سوبسید
- مابه التفاوت
- انتقال
- اصلاحیه


---

# حسابداری


حسابداری دوبل الزامی است.


مدل:


JournalEntry

شماره سند

+

JournalLine


---

# سیستم شماره سند ⭐


تمام اسناد باید شماره یکتا داشته باشند.


انواع شماره:


## قرارداد

مثال:

CTR-000001


## تراکنش مالی

مثال:

TRX-000001


## سند حسابداری

مثال:

JV-000001


## دریافت

RCV-000001


## پرداخت

PAY-000001


شماره سند:

- یکتا
- غیرقابل تغییر
- قابل جستجو


---

# قانون اصلاح اسناد


اسناد مالی حذف نمی‌شوند.


اصلاح:

با سند اصلاحی انجام می‌شود.


ثبت تاریخچه:

AuditLog


---

# Audit Log


ثبت:

- کاربر
- زمان
- عملیات
- جدول
- رکورد
- مقدار قبل
- مقدار بعد


---

# Import


نسخه اول دارای Import ساده است.


کاربرد:

- صورتحساب بانک
- لیست اعضا
- واحدها


فرمت:

Excel

CSV


بدون ETL پیچیده.


---

# Backup


الزامی:


- Backup PostgreSQL
- Export Excel
- Restore


---

# گردش عضو


Customer

↓

ProjectMember

↓

Membership Contract

↓

ایجاد بدهی پلن پروژه

↓

ثبت وام/سوبسید

↓

ثبت پرداخت

↓

انتخاب واحد

↓

Final Contract

↓

محاسبه مابه التفاوت


---

# قوانین مالی


وام و سوبسید متعلق به شخص است.


فرمول:


بدهی واقعی عضو

=

بدهی قرارداد

-

آورده‌ها



---

# Service Layer


نسخه اول:


Router

↓

Service

↓

Model



بدون:

- Repository Pattern
- Event System
- CQRS


---

# MVP Tables


Customer

Project

ProjectMember

Unit

Contract

Account

FinancialTransaction

JournalEntry

JournalLine

DynamicField

DynamicValue

AuditLog

DocumentNumber


---

# Roadmap بعدی


Sprint بعد:


- ایجاد پروژه FastAPI
- Migration
- CRUD پایه
- فرم‌ها
- ثبت عضو
- ثبت قرارداد
- ایجاد بدهی خودکار
- ثبت پرداخت
- سند حسابداری خودکار


---

# خارج از نسخه اول


- Plugin System
- Workflow
- BI
- Mobile App
- پیامک
- انبار
- حقوق
- مالیات
- حسابداری صنعتی


---

# دستور برای Code Agent


این سند مرجع اصلی پروژه است.

هدف:

ساخت سریع یک سیستم عملیاتی کوچک، پایدار و قابل توسعه.


قبل از اضافه کردن هر قابلیت:

بررسی شود:

آیا برای MVP ضروری است؟

اگر نه:

به Roadmap منتقل شود.