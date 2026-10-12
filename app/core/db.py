from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# postgres connection url
DB_URL = "postgresql://neondb_owner:npg_YSeoh4uJCp8N@ep-noisy-base-b4nmjeou-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# create engine
# pool_pre_ping: test each pooled connection before use and reconnect if Neon closed it
# pool_recycle: drop connections older than 5 min (Neon suspends idle computes / drops idle SSL connections)
engine = create_engine(
    DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

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