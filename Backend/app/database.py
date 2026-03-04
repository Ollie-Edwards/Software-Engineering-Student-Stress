import sqlalchemy as _sql
from sqlalchemy.orm import declarative_base
import sqlalchemy.orm as _orm
import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Prefer explicit DATABASE_URL, otherwise build from POSTGRES_* env vars
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER")
    pwd = os.getenv("POSTGRES_PASSWORD")
    dbname = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    if user and pwd and dbname:
        DATABASE_URL = f"postgresql://{user}:{pwd}@{host}:{port}/{dbname}"

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured; set it in the environment or .env file"
    )

engine = _sql.create_engine(DATABASE_URL)

SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
