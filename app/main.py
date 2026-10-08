
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.db import Base, engine, sessionLocal
from app.modules.users.service import create_superadmin
from app.core.logging import setup_logging
from app.register_routes import combine_router


# setup logging
setup_logging()
logger = logging.getLogger(__name__)


# create FastAPI instance
app = FastAPI(
    title="Enterprise FastAPI Application",
    description="This is a FastAPI application with PostgreSQL integration and modular architecture.",
)


# allow requests from localhost (any port)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# create database tables
Base.metadata.create_all(bind=engine)

# create_all does not add new columns to existing tables
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'"))


# startup event to log application startup
@app.on_event("startup")
async def startup_event():
    db = sessionLocal()
    try:
        create_superadmin(db)
    finally:
        db.close()
    logger.info("Application startup: Database tables created and logging configured.")


# shutdown event to log application shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: Cleanup tasks completed.")


# create a root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {
        "success": True,
        "message": "Welcome to the FastAPI application!"
    }


# include the combined router
app.include_router(combine_router)




