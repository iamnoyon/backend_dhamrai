from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .service import get_wards

router = APIRouter(prefix="/ward", tags=["Ward"])

@router.get("/list", summary="Get all wards")
async def list_wards(db: Session = Depends(get_db)):
    return await get_wards(db)