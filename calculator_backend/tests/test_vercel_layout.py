import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from calculator_backend.app.database import database
from dev import app as local_app


ROOT = Path(__file__).resolve().parents[2]


def test_vercel_static_assets_and_api_routes_are_separate():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    assert config["framework"] == "fastapi"
    assert config["rewrites"] == [{"source": "/", "destination": "/index.html"}]
    for path in ["index.html", "css/style.css", "js/app.js"]:
        assert (ROOT / "public" / path).read_bytes() == (ROOT / "calculator_frontend" / path).read_bytes()
    assert 'const API_BASE = "/api"' in (ROOT / "public/js/app.js").read_text(encoding="utf-8")


def test_local_same_origin_serves_page_assets_and_api(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'browser.db'}")
    monkeypatch.setattr(database, "get_engine", lambda: engine)
    with TestClient(local_app) as client:
        assert client.get("/").status_code == 200
        assert "text/html" in client.get("/").headers["content-type"]
        assert client.get("/css/style.css").status_code == 200
        assert client.get("/js/app.js").status_code == 200
        response = client.post("/api/calculate", json={"expression": "(1+2)*3"})
        assert response.status_code == 200
        assert response.json()["result"] == 9
        assert len(client.get("/api/history").json()["data"]) == 1
    engine.dispose()
