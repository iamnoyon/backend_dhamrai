from .model import Upazila
from sqlalchemy.orm import Session

async def get_upazilas(db: Session):
    return db.query(Upazila).all()