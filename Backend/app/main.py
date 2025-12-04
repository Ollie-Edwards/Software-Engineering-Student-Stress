from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from database import Base, engine, get_db
from models.user import User
from models.task import Task
from models.subtask import Subtask

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from database import DATABASE_URL

engine = create_engine(DATABASE_URL)
while True:
    try:
        conn = engine.connect()
        conn.close()
        break
    except OperationalError:
        print("Database not ready, retrying in 2s...")
        time.sleep(2)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks
