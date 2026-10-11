import logging
from .model import Ward
from app.modules.union.model import Union
from sqlalchemy.orm import Session

logger = logging.getLogger("Ward::Service")

async def get_wards(db: Session):
    logger.info("Fetching all wards from the database")
    return db.query(Ward).all()

# Service function for the ward dropdown, optionally of one union, wards have no name so it is built from the ward number
async def get_ward_dropdown(union_id, db: Session):
    query = (
        db.query(Ward.id, Ward.ward_no, Ward.code, Ward.union_id, Union.upazila_id)
        .join(Union, Union.id == Ward.union_id)
    )
    if union_id is not None:
        query = query.filter(Ward.union_id == union_id)

    return {
        "success": True,
        "message": "Ward dropdown list",
        "data": [
            {
                "id": w.id,
                "name": f"Ward {w.ward_no}",
                "ward_no": w.ward_no,
                "ward_code": w.code,
                "union_id": w.union_id,
                "upazila_id": w.upazila_id,
            }
            for w in query.order_by(Ward.union_id, Ward.ward_no).all()
        ]
    }
