from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.core.logging_config import setup_logging
from app.ingest_slack import router as slack_router
from app.ingest_dictation import router as dictation_router
from app.api_review import router as review_router

# -------------------------------------------------
# Logging
# -------------------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)

# -------------------------------------------------
# FastAPI App (BOOTSTRAP SAFE)
# -------------------------------------------------
app = FastAPI(
    title="LifeOS Tasks",
    description="Bootstrap-safe API",
    version="0.1.0",
)

# -------------------------------------------------
# Routers (NO DATABASE)
# -------------------------------------------------
app.include_router(slack_router)
app.include_router(dictation_router)
app.include_router(review_router)

# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# Static Frontend
# -------------------------------------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")
