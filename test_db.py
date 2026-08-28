import pytest

sqlalchemy = pytest.importorskip("sqlalchemy", reason="SQLAlchemy is required for database smoke tests")

from app.core.database import engine
from sqlalchemy import text


def test_database_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
