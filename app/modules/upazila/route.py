from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db

from .service import get_upazilas

router = APIRouter(prefix="/upazila", tags=["Upazila"])


@router.get("/list", summary="Get all upazilas")
async def get_upazilas(db: Session = Depends(get_db)):
    return await get_upazilas(db)
