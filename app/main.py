import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.sqlite import init_db
from app.routers import admin, auth, claim, health, onboarding, pages, quizzes

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url=None,
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(claim.router)
app.include_router(onboarding.router)
app.include_router(pages.router)
app.include_router(quizzes.router)
app.include_router(admin.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
        },
    )
