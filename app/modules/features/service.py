import logging
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
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


async def get_feature_dropdown(db: Session):
    features = (
        db.query(Feature.id, Feature.title)
        .filter(Feature.status == "active")
        .all()
    )

    return {
        "success": True,
        "message": "Feature dropdown list",
        "data": [
            {
                "id": feature.id,
                "title": feature.title
            }
            for feature in features
        ]
    }


# Service funtion to get feature by id
async def get_featureById(id, db: Session):
    feature = db.query(Feature).filter(Feature.id == id).first()

    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found!"
        )

    # Union names by id, for the feature's union and every ward's union
    union_ids = {w["union_id"] for w in feature.wards}
    if feature.union_id is not None:
        union_ids.add(feature.union_id)
    union_names = dict(db.query(Union.id, Union.name).filter(Union.id.in_(union_ids)).all())

    return {
        "success": True,
        "message": "Feature retrive by id",
        "data": {
            "id": feature.id,
            "title": feature.title,
            "is_union_based": feature.is_union_based,
            "union_id": feature.union_id,
            "union_name": union_names.get(feature.union_id),
            "status": feature.status,
            "candidates": feature.candidates,
            "wards": [
                {**w, "union_name": union_names.get(w["union_id"])}
                for w in feature.wards
            ],
            "created_at": feature.created_at,
            "updated_at": feature.updated_at,
        }
    }


# Service function to update a feature's candidates and its wards' total voters
async def update_feature_service(id: int, req, db: Session):
    feature = db.get(Feature, id)
    if feature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found!"
        )

    # Total voters, a ward is matched by (union_id, ward_id), ward_id is null for a union without wards
    if req.wards is not None:
        voters = {(w.union_id, w.ward_id): w.total_voter for w in req.wards}
        known = {(w["union_id"], w["ward_id"]) for w in feature.wards}
        missing = [key for key in voters if key not in known]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wards not found in this feature (union_id, ward_id): {missing}"
            )
        # Assign a new list so the json change is saved
        feature.wards = [
            {**w, "total_voter": voters.get((w["union_id"], w["ward_id"]), w["total_voter"])}
            for w in feature.wards
        ]

    # Candidates, the list replaces the old one: existing id updates, new id or no id adds, left out removes
    if req.candidates is not None:
        existing_ids = {c["id"] for c in feature.candidates}

        # Candidates without id get the next unused keys
        used_ids = existing_ids | {c.id for c in req.candidates if c.id is not None}
        candidates = []
        index = 0
        for c in req.candidates:
            candidate_id = c.id
            if candidate_id is None:
                while candidate_key(index) in used_ids:
                    index += 1
                candidate_id = candidate_key(index)
                used_ids.add(candidate_id)
            candidates.append({"id": candidate_id, "name": c.name, "image": c.image})

        # Results of removed candidates are deleted
        removed_ids = existing_ids - {c["id"] for c in candidates}
        if removed_ids:
            db.query(FeatureResult).filter(
                FeatureResult.feature_id == feature.id,
                FeatureResult.candidate_id.in_(removed_ids)
            ).delete(synchronize_session=False)

        feature.candidates = candidates

    db.commit()

    logger.info(f"Feature updated: {feature.id} - {feature.title}")

    response = await get_featureById(feature.id, db)
    response["message"] = "Feature updated successfully"
    return response




# Service function to create a feature with its wards and candidates
async def create_feature_service(req, db: Session):
    # Check the title is not already used (case-insensitive)
    duplicate_title = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Feature with title '{req.title}' already exists"
    )
    if db.query(Feature).filter(func.lower(Feature.title) == req.title.lower()).first() is not None:
        raise duplicate_title

    # Union based feature takes its own union, otherwise every union
    if req.is_union_based:
        union = db.get(Union, req.union_id)
        if union is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Union {req.union_id} not found"
            )
        unions = [union]
    else:
        unions = db.query(Union).order_by(Union.id).all()
        if not unions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No unions found"
            )

    # Wards of those unions, grouped by union
    wards_by_union = {}
    wards = db.query(Ward).filter(Ward.union_id.in_([u.id for u in unions])).order_by(Ward.ward_no).all()
    for ward in wards:
        wards_by_union.setdefault(ward.union_id, []).append(ward)

    # A union with wards gets one entry per ward, a union without wards (paurashava) gets one direct entry
    entries = []
    for union in unions:
        union_wards = wards_by_union.get(union.id)
        if union_wards:
            entries.extend(
                {"ward_id": ward.id, "code": ward.code, "union_id": union.id, "ward_no": ward.ward_no, "total_voter": 0}
                for ward in union_wards
            )
        else:
            entries.append({"ward_id": None, "code": None, "union_id": union.id, "ward_no": None, "total_voter": 0})

    # Create the feature, wards and candidates are stored as json
    feature = Feature(
        title = req.title,
        is_union_based = req.is_union_based,
        union_id = req.union_id,
        wards = entries,
        candidates = [
            {"id": candidate_key(i), "name": c.name, "image": c.image}
            for i, c in enumerate(req.candidates)
        ]
    )
    db.add(feature)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise duplicate_title
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

    if req.ward_code is None:
        # No ward code, the union must be a union without wards (paurashava) in this feature
        ward = next((w for w in feature.wards if w["union_id"] == req.union_id and w["ward_id"] is None), None)
        if ward is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Union {req.union_id} has no direct entry in this feature, ward_code is required"
            )
    elif feature.is_union_based:
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
    else:
        # Not union based, ward code is enough to find the ward in this feature
        ward = next((w for w in feature.wards if w["code"] == req.ward_code), None)
        if ward is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ward {req.ward_code} not found for this feature"
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
        FeatureResult.union_id == ward["union_id"],
        FeatureResult.ward_id.is_(None) if ward["ward_id"] is None else FeatureResult.ward_id == ward["ward_id"],
        FeatureResult.candidate_id == candidate["id"]
    ).first()

    if result is None:
        result = FeatureResult(
            feature_id = feature.id,
            union_id = ward["union_id"],
            ward_id = ward["ward_id"],
            candidate_id = candidate["id"],
            value = req.value
        )
        db.add(result)
    else:
        result.value = req.value

    db.commit()

    logger.info(f"Result saved: feature {feature.id}, union {ward['union_id']}, ward {ward['code']}, candidate {candidate['id']} = {req.value}")

    return {
        "message": "Result saved successfully",
        "result": {
            "feature_id": feature.id,
            "union_id": ward["union_id"],
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

# Service function to get a feature's results grouped by ward code (union-<id> for a union without wards)
async def get_feature_result_service(feature_id: int, db: Session):
    # Check the feature exists
    feature = db.get(Feature, feature_id)
    if feature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found"
        )

    # Saved values by (union_id, ward_id, candidate_id)
    results = db.query(FeatureResult).filter(FeatureResult.feature_id == feature.id).all()
    values = {(r.union_id, r.ward_id, r.candidate_id): r.value for r in results}

    return {
        "feature_id": feature.id,
        "title": feature.title,
        "union_id": feature.union_id,
        "candidates": feature.candidates,
        "wards": {
            w["code"] or f"union-{w['union_id']}": {
                "union_id": w["union_id"],
                "wardNo": w["ward_no"],
                "totalVoters": w["total_voter"],
                "votes": {c["id"]: values.get((w["union_id"], w["ward_id"], c["id"]), 0) for c in feature.candidates},
            }
            for w in feature.wards
        },
    }
