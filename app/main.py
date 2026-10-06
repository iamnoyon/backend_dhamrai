
import logging

from fastapi import FastAPI
from app.core.db import Base, engine
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


# create database tables
Base.metadata.create_all(bind=engine)


# startup event to log application startup
@app.on_event("startup")
async def startup_event():
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




