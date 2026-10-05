from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# postgres connection url
DB_URL = "postgresql+psycopg://postgres:674@localhost:5432/enterprise_fastapi"

# create engine
engine = create_engine(DB_URL, echo=False)

# create session
sessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# create base class for models
class Base(DeclarativeBase):
    pass

# dependency to get db session
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()