import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select

from app import app
from calculator_backend.app.database import database
from calculator_backend.app.database.models import Base, CalculationHistory


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setattr(database, "get_engine", lambda: engine)
    yield engine
    engine.dispose()


def test_calculate_history_delete_and_clear(test_database):
    with TestClient(app) as client:
        assert client.get("/api/history").json()["data"] == []
        for expression, expected in [
            ("1+2", 3), ("1+2*3", 7), ("(1+2)*3", 9),
            ("3*-2", -6), ("3.14*2", 6.28),
        ]:
            response = client.post("/api/calculate", json={"expression": expression})
            assert response.status_code == 200
            assert response.json()["result"] == expected
        for expression in ["1/0", "1++*", ""]:
            response = client.post("/api/calculate", json={"expression": expression})
            assert response.status_code == 400
            assert response.json()["success"] is False
        records = client.get("/api/history").json()["data"]
        assert [row["expression"] for row in records] == [
            "3.14*2", "3*-2", "(1+2)*3", "1+2*3", "1+2",
        ]
        assert all(row["created_at"] for row in records)
        assert client.delete(f"/api/history/{records[0]['id']}").status_code == 200
        assert client.delete(f"/api/history/{records[0]['id']}").status_code == 404
        assert len(client.get("/api/history").json()["data"]) == 4
        assert client.delete("/api/history").status_code == 200
        assert client.get("/api/history").json()["data"] == []
    with test_database.connect() as connection:
        assert connection.execute(select(CalculationHistory)).all() == []


def test_history_survives_app_restart(test_database):
    with TestClient(app) as client:
        client.post("/api/calculate", json={"expression": "3.14*2"})
    with TestClient(app) as client:
        records = client.get("/api/history").json()["data"]
    assert len(records) == 1
    assert records[0]["result"] == 6.28


def test_startup_creates_history_table(test_database):
    with TestClient(app):
        pass
    assert "calculation_history" in Base.metadata.tables
    with test_database.connect() as connection:
        assert connection.dialect.has_table(connection, "calculation_history")


def test_scientific_result_is_saved_but_invalid_input_is_not(test_database):
    with TestClient(app) as client:
        response = client.post("/api/calculate", json={"expression": "sqrt(9)+2^3"})
        assert response.status_code == 200
        assert response.json()["result"] == 11
        invalid = client.post("/api/calculate", json={"expression": "sqrt(-1)"})
        assert invalid.status_code == 400
        history = client.get("/api/history").json()["data"]
        assert [(item["expression"], item["result"]) for item in history] == [("sqrt(9)+2^3", 11)]
