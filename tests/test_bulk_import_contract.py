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
