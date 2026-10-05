import os
import unittest
from datetime import date

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["AUTO_CREATE_SCHEMA"] = "true"

from app.core.database import Base, SessionLocal, engine
from app.models import Bank, BankAccount, BankStatement, Customer, Payment, PaymentStatus, Project, Receipt, ReceiptStatus, StatementType
from app.services.report_service import ReportService


class ManualBankReconciliationTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

        project = Project(project_code="T1", name="Test Project", start_date=date(2026, 10, 1))
        customer = Customer(customer_no="000001", full_name="Test Customer")
        bank = Bank(bank_name="Test Bank")
        self.db.add_all([project, customer, bank])
        self.db.flush()

        self.account = BankAccount(bank_id=bank.id, account_no="123456", account_name="Test Account")
        self.db.add(self.account)
        self.db.flush()

        self.receipt = Receipt(
            receipt_no="R-001", customer_id=customer.id, project_id=project.id,
            amount=100000, amount_in_words="", receipt_date=date(2026, 10, 5),
            payment_method="TRANSFER", bank_account_id=self.account.id,
            status=ReceiptStatus.CONFIRMED,
        )
        self.payment = Payment(
            payment_no="P-001", project_id=project.id, payee_name="Test Payee",
            amount=75000, payment_date=date(2026, 10, 5),
            bank_account_id=self.account.id, status=PaymentStatus.CONFIRMED,
        )
        self.db.add_all([self.receipt, self.payment])
        self.db.flush()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def test_receipt_reconciliation_and_unreconciliation(self):
        statement = BankStatement(
            bank_account_id=self.account.id, statement_date=date(2026, 10, 5),
            amount=100000, statement_type=StatementType.DEPOSIT,
        )
        self.db.add(statement)
        self.db.commit()

        result = ReportService.reconcile_bank_statement(self.db, statement.id, receipt_id=self.receipt.id)
        self.assertTrue(result.is_reconciled)
        self.assertEqual(result.receipt_id, self.receipt.id)
        self.assertIsNone(result.payment_id)

        ReportService.unreconcile_bank_statement(self.db, statement.id)
        self.assertFalse(result.is_reconciled)

    def test_payment_reconciliation(self):
        statement = BankStatement(
            bank_account_id=self.account.id, statement_date=date(2026, 10, 5),
            amount=75000, statement_type=StatementType.WITHDRAWAL,
        )
        self.db.add(statement)
        self.db.commit()

        result = ReportService.reconcile_bank_statement(self.db, statement.id, payment_id=self.payment.id)
        self.assertTrue(result.is_reconciled)
        self.assertEqual(result.payment_id, self.payment.id)
        self.assertIsNone(result.receipt_id)

    def test_mismatch_is_rejected(self):
        statement = BankStatement(
            bank_account_id=self.account.id, statement_date=date(2026, 10, 5),
            amount=99999, statement_type=StatementType.DEPOSIT,
        )
        self.db.add(statement)
        self.db.commit()

        with self.assertRaisesRegex(ValueError, "مبلغ و تاریخ"):
            ReportService.reconcile_bank_statement(self.db, statement.id, receipt_id=self.receipt.id)

    def test_second_bank_statement_cannot_reuse_same_receipt(self):
        first = BankStatement(
            bank_account_id=self.account.id, statement_date=date(2026, 10, 5),
            amount=100000, statement_type=StatementType.DEPOSIT,
        )
        second = BankStatement(
            bank_account_id=self.account.id, statement_date=date(2026, 10, 5),
            amount=100000, statement_type=StatementType.DEPOSIT,
        )
        self.db.add_all([first, second])
        self.db.commit()

        ReportService.reconcile_bank_statement(self.db, first.id, receipt_id=self.receipt.id)

        with self.assertRaisesRegex(ValueError, "قبلاً"):
            ReportService.reconcile_bank_statement(self.db, second.id, receipt_id=self.receipt.id)


if __name__ == "__main__":
    unittest.main()
