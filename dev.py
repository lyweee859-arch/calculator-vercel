from pathlib import Path

from fastapi.staticfiles import StaticFiles

from calculator_backend.app.main import app


app.mount("/", StaticFiles(directory=Path(__file__).parent / "public", html=True))
