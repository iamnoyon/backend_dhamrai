import logging
from .model import Ward
from sqlalchemy.orm import Session

logger = logging.getLogger("Ward::Service")

async def get_wards(db: Session):
    logger.info("Fetching all wards from the database")
    return db.query(Ward).all()