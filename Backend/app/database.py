import sqlalchemy as _sql
from sqlalchemy.orm import declarative_base
import sqlalchemy.orm as _orm
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
