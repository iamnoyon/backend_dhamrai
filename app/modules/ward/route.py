from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .service import get_wards, get_ward_dropdown

router = APIRouter(prefix="/ward", tags=["Ward"])

@router.get("/list", summary="Get all wards")
async def list_wards(db: Session = Depends(get_db)):
    return await get_wards(db)

@router.get("/dropdown", summary="Dropdown list for wards")
async def dropdown_ward(union_id: Optional[int] = None, db: Session = Depends(get_db)):
    return await get_ward_dropdown(union_id, db)
