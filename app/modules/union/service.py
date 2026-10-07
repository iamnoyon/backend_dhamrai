import logging
from .model import Union
from sqlalchemy.orm import Session

logger = logging.getLogger("Union::Service")

async def get_unions(db: Session):
    logger.info("Fetching all unions from the database")
    return db.query(Union).all()