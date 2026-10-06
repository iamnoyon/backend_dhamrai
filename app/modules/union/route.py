from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .service import get_unions


router = APIRouter(prefix="/union", tags=["Union"])


@router.get("/list", summary="Get all unions")
async def list_unions(db: Session = Depends(get_db)):
    return await get_unions(db)