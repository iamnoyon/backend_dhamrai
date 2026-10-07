from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from .schema import FeatureCreateSchema, FeatureResultSchema
from .service import (
    get_features, 
    create_feature_service, 
    update_feature_result_service, 
    get_feature_results, 
    get_feature_result_service,
    get_feature_dropdown
)

router = APIRouter(prefix="/feature", tags=["Feature"])

@router.get("/list", summary="Get all features")
async def list_features(db: Session = Depends(get_db)):
    return await get_features(db)

@router.get('/dropdown', summary="Dropdown list for features")
async def dropdown_feature(db: Session = Depends(get_db)):
    return await get_feature_dropdown(db)


@router.post("/create", summary="Create a feature with wards and candidates")
async def create_feature(req: FeatureCreateSchema, db: Session = Depends(get_db)):
    return await create_feature_service(req, db)


@router.put("/result", summary="Add or update a candidate's value for a ward")
async def update_feature_result(req: FeatureResultSchema, db: Session = Depends(get_db)):
    return await update_feature_result_service(req, db)

@router.get("/result/list", summary="Get all feature results")
async def list_feature_results(db: Session = Depends(get_db)):
    return await get_feature_results(db)


@router.get("/result/{feature_id}", summary="Get results of a feature")
async def feature_result(feature_id: int, db: Session = Depends(get_db)):
    return await get_feature_result_service(feature_id, db)
