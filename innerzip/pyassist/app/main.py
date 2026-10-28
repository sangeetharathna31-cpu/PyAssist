import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from pyassist.app.config import settings
from pyassist.app.database import init_db, get_db
from pyassist.app.schemas import HealthResponse
from pyassist.app.routes import authentication, chat, history

# Path to static folder
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="PyAssist API",
    description="Personal Python Question-Answering Chatbot Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Register API routers
app.include_router(authentication.router)
app.include_router(chat.router)
app.include_router(history.router)

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint confirming service status without leaking credentials or paths."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        app=settings.APP_NAME,
        version="1.0.0",
        database=db_status,
        timestamp=datetime.utcnow()
    )

# Static file serving & HTML entry points
if STATIC_DIR.exists():
    # Mount css, js, etc. assets
    if (STATIC_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(STATIC_DIR / "css")), name="css")
    if (STATIC_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(STATIC_DIR / "js")), name="js")

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.api_route("/index.html", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_index_html():
        return FileResponse(STATIC_DIR / "index.html")

    @app.api_route("/login", methods=["GET", "HEAD"], include_in_schema=False)
    @app.api_route("/login.html", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_login():
        return FileResponse(STATIC_DIR / "login.html")

    @app.api_route("/register", methods=["GET", "HEAD"], include_in_schema=False)
    @app.api_route("/register.html", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_register():
        return FileResponse(STATIC_DIR / "register.html")

# Global error handler to prevent internal trace leakage in production
@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    # In production, do not leak raw exception messages
    if settings.APP_ENV == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again."}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )
