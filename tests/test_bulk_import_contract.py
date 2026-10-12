import inspect

from app.services.bulk_import_service import BulkImportService


def test_bank_statement_bulk_import_is_dispatched_and_staged_without_committing():
    source = inspect.getsource(BulkImportService.process_bank_statement_bulk)
    dispatch = inspect.getsource(BulkImportService.process_bulk_import)

    assert "reference_no" in source
    assert "import_batch_id" in source
    assert "BankStatement" in source
    assert "StatementType" in source
    assert "db.commit()" not in source
    assert "BulkImportType.BANK_STATEMENT" in dispatch

def test_bank_statement_import_rejects_ambiguous_account_numbers():
    source = inspect.getsource(BulkImportService.process_bank_statement_bulk)
    assert "matching_accounts" in source
    assert "len(matching_accounts) > 1" in source
    assert "چند حساب بانکی مشترک است" in source


def test_bulk_import_upload_passes_selected_calendar_to_excel_parser():
    from app.routers.bulk_import import upload_excel
    from pathlib import Path

    import inspect

    source = inspect.getsource(upload_excel)
    template = Path("app/templates/bulk_import.html").read_text(encoding="utf-8")

    assert 'date_calendar: str = Form("jalali")' in source
    assert "date_calendar=date_calendar" in source
    assert 'name="date_calendar"' in template
    assert 'value="gregorian"' in template
