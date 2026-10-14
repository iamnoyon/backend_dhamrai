from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_superadmin
from .schema import DurgaPujaCreateSchema
from .service import create_durga_puja_service, get_durga_pujas, get_durga_puja_detail

router = APIRouter(prefix="/durga-puja", tags=["Durga Puja"])


@router.post("/create", summary="Add villages with their mondirs to a ward", dependencies=[Depends(get_current_superadmin)])
async def create_durga_puja(req: DurgaPujaCreateSchema, db: Session = Depends(get_db)):
    return await create_durga_puja_service(req, db)


@router.get("/list", summary="Get durga pujas of a feature with union name and ward number")
async def list_durga_pujas(feature_id: int, db: Session = Depends(get_db)):
    return await get_durga_pujas(feature_id, db)


@router.get("/detail", summary="Get durga puja details of a ward, ward_code is empty for a paurashava union")
async def durga_puja_detail(union_id: int, ward_code: Optional[str] = None, feature_id: Optional[int] = None, db: Session = Depends(get_db)):
    return await get_durga_puja_detail(union_id, ward_code, feature_id, db)
