from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .service import get_features

router = APIRouter(prefix="/feature", tags=["Feature"])

@router.get("/list", summary="Get all features")
async def list_features(db: Session = Depends(get_db)):
    return await get_features(db)