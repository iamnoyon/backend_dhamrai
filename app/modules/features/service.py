import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.union.model import Union
from app.modules.ward.model import Ward
from string import ascii_lowercase
from .model import Feature, FeatureResult

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


# Service function to add or update a candidate's value for a ward of a feature
async def update_feature_result_service(req, db: Session):
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

    # Check the ward exists in this feature's union
    ward = next((w for w in union_wards if w["code"] == req.ward_code), None)
    if ward is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ward {req.ward_code} not found in union {req.union_id} for this feature"
        )

    # Check the candidate exists in this feature
    name = req.candidate_name.strip().lower()
    candidate = next((c for c in feature.candidates if c["name"].strip().lower() == name), None)
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate '{req.candidate_name}' not found in this feature"
        )

    # Insert or update the value
    result = db.query(FeatureResult).filter(
        FeatureResult.feature_id == feature.id,
        FeatureResult.ward_id == ward["ward_id"],
        FeatureResult.candidate_id == candidate["id"]
    ).first()

    if result is None:
        result = FeatureResult(
            feature_id = feature.id,
            ward_id = ward["ward_id"],
            candidate_id = candidate["id"],
            value = req.value
        )
        db.add(result)
    else:
        result.value = req.value

    db.commit()

    logger.info(f"Result saved: feature {feature.id}, ward {ward['code']}, candidate {candidate['id']} = {req.value}")

    return {
        "message": "Result saved successfully",
        "result": {
            "feature_id": feature.id,
            "union_id": req.union_id,
            "ward_no": ward["ward_no"],
            "ward_code": ward["code"],
            "candidate_id": candidate["id"],
            "candidate_name": candidate["name"],
            "value": result.value,
        },
    }



async def get_feature_results(db: Session):
    logger.info("Fetching all feature results from the database")
    return db.query(FeatureResult).all()

# Service function to get a feature's results grouped by ward code
async def get_feature_result_service(feature_id: int, db: Session):
    # Check the feature exists
    feature = db.get(Feature, feature_id)
    if feature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found"
        )

    # Saved values by (ward_id, candidate_id)
    results = db.query(FeatureResult).filter(FeatureResult.feature_id == feature.id).all()
    values = {(r.ward_id, r.candidate_id): r.value for r in results}

    return {
        "feature_id": feature.id,
        "title": feature.title,
        "union_id": feature.union_id,
        "candidates": feature.candidates,
        "wards": {
            w["code"]: {
                "union_id": w["union_id"],
                "wardNo": w["ward_no"],
                "totalVoters": w["total_voter"],
                "votes": {c["id"]: values.get((w["ward_id"], c["id"]), 0) for c in feature.candidates},
            }
            for w in feature.wards
        },
    }
