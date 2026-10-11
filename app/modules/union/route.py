from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .service import get_unions, get_union_dropdown


router = APIRouter(prefix="/union", tags=["Union"])


@router.get("/list", summary="Get all unions")
async def list_unions(db: Session = Depends(get_db)):
    return await get_unions(db)

@router.get("/dropdown", summary="Dropdown list for unions")
async def dropdown_union(upazila_id: Optional[int] = None, db: Session = Depends(get_db)):
    return await get_union_dropdown(upazila_id, db)
