import logging
from .model import Union
from sqlalchemy.orm import Session

logger = logging.getLogger("Union::Service")

async def get_unions(db: Session):
    logger.info("Fetching all unions from the database")
    return db.query(Union).all()

# Service function for the union dropdown, optionally of one upazila
async def get_union_dropdown(upazila_id, db: Session):
    query = db.query(Union.id, Union.name, Union.upazila_id)
    if upazila_id is not None:
        query = query.filter(Union.upazila_id == upazila_id)

    return {
        "success": True,
        "message": "Union dropdown list",
        "data": [
            {"id": u.id, "name": u.name, "upazila_id": u.upazila_id}
            for u in query.order_by(Union.name).all()
        ]
    }
