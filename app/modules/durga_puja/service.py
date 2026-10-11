import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.union.model import Union
from app.modules.features.model import Feature
from .model import DurgaPuja

logger = logging.getLogger("DurgaPuja::Service")


# Service function to add villages with their mondirs to a ward of a feature's union
async def create_durga_puja_service(req, db: Session):
    # Check the feature exists
    feature = db.get(Feature, req.feature_id)
    if feature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {req.feature_id} not found"
        )

    # Check the union is part of this feature
    union_wards = [w for w in feature.wards if w["union_id"] == req.union_id]
    if not union_wards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Union {req.union_id} is not part of this feature"
        )

    # Check the ward is part of this feature's union, a union without wards (paurashava) has no ward code
    if not any(w["code"] == req.ward_code for w in union_wards):
        if req.ward_code is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Union {req.union_id} has wards in this feature, ward_code is required"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ward {req.ward_code} not found in union {req.union_id} for this feature"
        )

    villages = [v.model_dump() for v in req.villages]

    # One row per feature and ward, new villages are added to an existing row
    durga_puja = db.query(DurgaPuja).filter(
        DurgaPuja.feature_id == req.feature_id,
        DurgaPuja.union_id == req.union_id,
        DurgaPuja.ward_code.is_(None) if req.ward_code is None else DurgaPuja.ward_code == req.ward_code
    ).first()

    if durga_puja is None:
        durga_puja = DurgaPuja(
            feature_id = req.feature_id,
            union_id = req.union_id,
            ward_code = req.ward_code,
            villages = villages
        )
        db.add(durga_puja)
    else:
        # Check the same mondir is not already in the same village
        existing = {(v["village_name"].lower(), v["mondir_name"].lower()) for v in durga_puja.villages}
        for v in villages:
            if (v["village_name"].lower(), v["mondir_name"].lower()) in existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Mondir '{v['mondir_name']}' already exists in village '{v['village_name']}'"
                )

        # Assign a new list so the json change is saved
        durga_puja.villages = durga_puja.villages + villages

    db.commit()
    db.refresh(durga_puja)

    logger.info(f"Durga puja saved: feature {durga_puja.feature_id}, union {durga_puja.union_id}, ward {durga_puja.ward_code}, {len(villages)} village(s) added")

    return {
        "success": True,
        "message": "Durga puja created successfully",
        "data": durga_puja
    }


# Service function to list every union's every ward of a feature with its villages, empty villages when nothing is saved yet
async def get_durga_pujas(feature_id: int, db: Session):
    # Check the feature exists
    feature = db.get(Feature, feature_id)
    if feature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found"
        )

    # Saved rows by (union_id, ward_code), ward_code is null for a union without wards (paurashava)
    saved = {
        (d.union_id, d.ward_code): d
        for d in db.query(DurgaPuja).filter(DurgaPuja.feature_id == feature_id).all()
    }

    union_ids = {w["union_id"] for w in feature.wards}
    union_names = dict(db.query(Union.id, Union.name).filter(Union.id.in_(union_ids)).all())

    # Sorted by union name, then ward number (a union without wards first)
    wards = sorted(
        feature.wards,
        key=lambda w: (union_names.get(w["union_id"]) or "", w["ward_no"] is not None, w["ward_no"] or 0)
    )

    data = []
    for w in wards:
        durga_puja = saved.get((w["union_id"], w["code"]))
        data.append({
            "id": durga_puja.id if durga_puja else None,  # null until the first village is added
            "feature_id": feature.id,
            "union_id": w["union_id"],
            "union_name": union_names.get(w["union_id"]),
            "ward_code": w["code"],
            "ward_no": w["ward_no"],
            "villages": durga_puja.villages if durga_puja else [],
            "created_at": durga_puja.created_at if durga_puja else None,
            "updated_at": durga_puja.updated_at if durga_puja else None,
        })

    return {
        "success": True,
        "message": "Durga puja list",
        "data": data
    }
