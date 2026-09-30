from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, inspect, text


@pytest.mark.postgres
def test_postgres_runtime_schema_contract():
    url = os.getenv("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("TEST_POSTGRES_URL is not configured")
    engine = create_engine(url, pool_pre_ping=True)
    assert engine.dialect.name == "postgresql"
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT 1")) == 1
    tables = set(inspect(engine).get_table_names())
    assert {"organizations", "users", "refresh_sessions", "products", "inventory_items", "audit_events"}.issubset(tables)
