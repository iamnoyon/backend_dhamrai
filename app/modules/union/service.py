from .model import Union
from sqlalchemy.orm import Session

async def get_unions(db: Session):
    return db.query(Union).all()