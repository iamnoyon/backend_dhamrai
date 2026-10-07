from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .schema import FeatureCreateSchema, FeatureResultSchema
from .service import get_features, create_feature_service, update_feature_result_service

router = APIRouter(prefix="/feature", tags=["Feature"])

@router.get("/list", summary="Get all features")
async def list_features(db: Session = Depends(get_db)):
    return await get_features(db)


@router.post("/create", summary="Create a feature with wards and candidates")
async def create_feature(req: FeatureCreateSchema, db: Session = Depends(get_db)):
    return await create_feature_service(req, db)


@router.put("/result", summary="Add or update a candidate's value for a ward")
async def update_feature_result(req: FeatureResultSchema, db: Session = Depends(get_db)):
    return await update_feature_result_service(req, db)
