from .model import Ward
from sqlalchemy.orm import Session

async def get_wards(db: Session):
    return db.query(Ward).all()