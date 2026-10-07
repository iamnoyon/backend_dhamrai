import logging
from .model import Upazila
from sqlalchemy.orm import Session

logger = logging.getLogger("Upazila::Service")

async def get_upazilas(db: Session):
    logger.info("Fetching all upazilas from the database")
    return db.query(Upazila).all()