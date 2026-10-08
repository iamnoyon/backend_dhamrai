from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# postgres connection url
DB_URL = "postgresql://neondb_owner:npg_YSeoh4uJCp8N@ep-noisy-base-b4nmjeou-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

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