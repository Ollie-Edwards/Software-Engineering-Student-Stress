import time

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.database import Base, engine, get_db, DATABASE_URL
from app.models.user import User  # add this
from app.models.task import Task  # add this
from app.models.subtask import Subtask  # add this
from app.schemas import TaskResponse
from app.tasks import router as tasks_router
from app.reminders import router as reminders_router

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

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(reminders_router, prefix="/reminders", tags=["reminders"])
