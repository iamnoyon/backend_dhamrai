from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .schema import FeatureCreateSchema
from .service import get_features, create_feature_service

router = APIRouter(prefix="/feature", tags=["Feature"])

@router.get("/list", summary="Get all features")
async def list_features(db: Session = Depends(get_db)):
    return await get_features(db)


@router.post("/create", summary="Create a feature with wards and candidates")
async def create_feature(req: FeatureCreateSchema, db: Session = Depends(get_db)):
    return await create_feature_service(req, db)
