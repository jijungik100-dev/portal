from fastapi import FastAPI

from app.config import get_settings
from app.routers import datasets, health, home

settings = get_settings()

app = FastAPI(
    title="Data Portal API",
    version="0.1.0",
    docs_url="/docs" if settings.env != "prod" else None,
    redoc_url=None,
)

# --- Routers ---
app.include_router(health.router)
app.include_router(home.router)
app.include_router(datasets.router)
