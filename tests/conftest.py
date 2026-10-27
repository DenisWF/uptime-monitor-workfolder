import os
from pathlib import Path

import psycopg
import pytest

from app.storage import Storage

SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "001_schema.sql"


@pytest.fixture
def db_dsn():
    dsn = os.environ.get("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL не задан")
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(SCHEMA.read_text(encoding="utf-8"))
        conn.execute("TRUNCATE checks, targets RESTART IDENTITY CASCADE")
    return dsn


@pytest.fixture
def storage(db_dsn):
    s = Storage(db_dsn)
    yield s
    s.close()