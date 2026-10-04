import pytest
from unittest.mock import patch

from calculator_backend.app.database.database import _engine_for_url, get_engine, normalize_database_url
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from calculator_backend.app.database.models import CalculationHistory


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("postgres://user:pass@host/db", "postgresql+psycopg://user:pass@host/db"),
        ("postgresql://user:pass@host/db", "postgresql+psycopg://user:pass@host/db"),
        ("postgresql+psycopg://user:pass@host/db?sslmode=require", "postgresql+psycopg://user:pass@host/db?sslmode=require"),
    ],
)
def test_postgres_url_is_normalized(source, expected):
    assert normalize_database_url(source) == expected


@pytest.mark.parametrize("source", ["", "sqlite:///tmp/test.db", "mysql://host/db"])
def test_missing_or_non_postgres_url_is_rejected(source):
    with pytest.raises(ValueError, match="DATABASE_URL"):
        normalize_database_url(source)


def test_postgres_engine_uses_psycopg_without_connecting(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost/example")
    engine = get_engine()
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg"
    engine.dispose()


def test_schema_compiles_for_postgres():
    statement = str(CreateTable(CalculationHistory.__table__).compile(dialect=postgresql.dialect()))
    assert "CREATE TABLE calculation_history" in statement
    assert "TIMESTAMP WITH TIME ZONE" in statement


def test_pooled_postgres_disables_prepared_statements():
    _engine_for_url.cache_clear()
    with patch("calculator_backend.app.database.database.create_engine") as factory:
        _engine_for_url("postgresql+psycopg://user:pass@host/db")
        assert factory.call_args.kwargs["connect_args"]["prepare_threshold"] is None
    _engine_for_url.cache_clear()
