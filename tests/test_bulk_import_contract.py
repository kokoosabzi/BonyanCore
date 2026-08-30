from pathlib import Path


def test_bank_statement_import_keeps_required_preview_fields():
    template = Path("app/templates/bulk_import_preview.html").read_text(encoding="utf-8")
    for field in ("date", "account_no", "transaction_type", "reference_no"):
        assert f"][{field}]" in template


def test_bulk_import_supports_explicit_date_calendar():
    schema = Path("app/schemas/bulk_import.py").read_text(encoding="utf-8")
    router = Path("app/routers/bulk_import.py").read_text(encoding="utf-8")
    excel_service = Path("app/services/excel_service.py").read_text(encoding="utf-8")

    assert "class DateCalendar" in schema
    assert "date_calendar" in router
    assert "date_calendar" in excel_service
    assert "parse_jalali_date" in excel_service


def test_startup_schema_creation_is_flag_gated():
    main = Path("main.py").read_text(encoding="utf-8")
    config = Path("app/core/config.py").read_text(encoding="utf-8")
    database = Path("app/core/database.py").read_text(encoding="utf-8")

    assert "AUTO_CREATE_TABLES" in config
    assert "if settings.AUTO_CREATE_TABLES:" in main
    assert "echo=settings.SQL_ECHO" in database
