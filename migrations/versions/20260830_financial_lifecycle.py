"""financial lifecycle tables and receipt cheque fields

Revision ID: 20260830_financial_lifecycle
Revises:
Create Date: 2026-08-30
"""
from alembic import op
import sqlalchemy as sa
revision = "20260830_financial_lifecycle"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("receipts", sa.Column("cheque_status", sa.String(30), nullable=True))
    op.add_column("receipts", sa.Column("cheque_collected_at", sa.Date(), nullable=True))
    op.add_column("receipts", sa.Column("cheque_returned_at", sa.Date(), nullable=True))
    op.add_column("receipts", sa.Column("cheque_return_reason", sa.Text(), nullable=True))
    op.create_table("receipt_allocations", sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("receipt_id", sa.BigInteger(), nullable=False), sa.Column("obligation_id", sa.BigInteger(), nullable=False), sa.Column("allocated_amount", sa.BigInteger(), nullable=False), sa.Column("allocated_at", sa.Date(), nullable=False), sa.ForeignKeyConstraint(["receipt_id"],["receipts.id"]), sa.ForeignKeyConstraint(["obligation_id"],["financial_obligations.id"]), sa.UniqueConstraint("receipt_id", "obligation_id", name="uq_receipt_obligation"))
    op.create_table("bank_reconciliation_matches", sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("bank_statement_id", sa.BigInteger(), nullable=False), sa.Column("source_type", sa.String(30), nullable=False), sa.Column("source_id", sa.BigInteger(), nullable=False), sa.Column("matched_at", sa.Date(), nullable=False), sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default=sa.false()), sa.ForeignKeyConstraint(["bank_statement_id"],["bank_statements.id"]), sa.UniqueConstraint("bank_statement_id", name="uq_bank_statement_match"))
def downgrade():
    op.drop_table("bank_reconciliation_matches"); op.drop_table("receipt_allocations")
    op.drop_column("receipts", "cheque_return_reason"); op.drop_column("receipts", "cheque_returned_at"); op.drop_column("receipts", "cheque_collected_at"); op.drop_column("receipts", "cheque_status")
