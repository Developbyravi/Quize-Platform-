from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.logging import setup_logging, log_event
from app.utils.seed_data import seed_database

# Routers
from app.api.auth import router as auth_router
from app.api.rounds import router as rounds_router
from app.api.quiz import router as quiz_router
from app.api.code import router as code_router
from app.api.leaderboard import router as leaderboard_router
from app.api.violations import router as violations_router
from app.api.admin import router as admin_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables & seed initial competition data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.SUBTITLE,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(rounds_router, prefix=settings.API_V1_STR)
app.include_router(quiz_router, prefix=settings.API_V1_STR)
app.include_router(code_router, prefix=settings.API_V1_STR)
app.include_router(leaderboard_router, prefix=settings.API_V1_STR)
app.include_router(violations_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "title": settings.PROJECT_NAME,
        "subtitle": settings.SUBTITLE,
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
