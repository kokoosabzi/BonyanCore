"""manual bank reconciliation links

Revision ID: 20261005_manual_bank_reconciliation
Revises: 3554422ca1ec
Create Date: 2026-10-05
"""
from alembic import op
import sqlalchemy as sa

revision = "20261005_manual_bank_reconciliation"
down_revision = "3554422ca1ec"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("bank_statements", sa.Column("receipt_id", sa.BigInteger(), nullable=True))
    op.add_column("bank_statements", sa.Column("payment_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key("fk_bank_statements_receipt_id", "bank_statements", "receipts", ["receipt_id"], ["id"])
    op.create_foreign_key("fk_bank_statements_payment_id", "bank_statements", "payments", ["payment_id"], ["id"])
    op.create_unique_constraint("uq_bank_statement_receipt", "bank_statements", ["receipt_id"])
    op.create_unique_constraint("uq_bank_statement_payment", "bank_statements", ["payment_id"])

def downgrade():
    op.drop_constraint("uq_bank_statement_payment", "bank_statements", type_="unique")
    op.drop_constraint("uq_bank_statement_receipt", "bank_statements", type_="unique")
    op.drop_constraint("fk_bank_statements_payment_id", "bank_statements", type_="foreignkey")
    op.drop_constraint("fk_bank_statements_receipt_id", "bank_statements", type_="foreignkey")
    op.drop_column("bank_statements", "payment_id")
    op.drop_column("bank_statements", "receipt_id")
