import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.union.model import Union
from app.modules.ward.model import Ward
from string import ascii_lowercase
from .model import Feature

logger = logging.getLogger("Feature::Service")

async def get_features(db: Session):
    logger.info("Fetching all features from the database")
    return db.query(Feature).all()


# Service function to create a feature with its wards and candidates
async def create_feature_service(req, db: Session):
    # Check the union exists for union based feature
    if req.is_union_based and db.get(Union, req.union_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Union {req.union_id} not found"
        )

    # Resolve each ward by union_id + ward_no
    wards = []
    for w in req.wards:
        ward = db.query(Ward).filter(Ward.union_id == w.union_id, Ward.ward_no == w.ward_no).first()
        if ward is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ward {w.ward_no} not found in union {w.union_id}"
            )
        wards.append((ward, w.total_voter))

    # Create the feature, wards and candidates are stored as json
    feature = Feature(
        title = req.title,
        is_union_based = req.is_union_based,
        union_id = req.union_id,
        wards = [
            {"ward_id": ward.id, "code": ward.code, "union_id": ward.union_id, "ward_no": ward.ward_no, "total_voter": total}
            for ward, total in wards
        ],
        candidates = [
            {"id": candidate_key(i), "name": c.name, "image": c.image}
            for i, c in enumerate(req.candidates)
        ]
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)

    logger.info(f"New feature created: {feature.id} - {feature.title}")

    return {"message": "Feature created successfully", "feature": feature}


# Candidate key like a, b, ..., z, aa, ab, ...
def candidate_key(index: int) -> str:
    key = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        key = ascii_lowercase[rem] + key
    return key
