import time

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.database import Base, engine, get_db, DATABASE_URL

# These are required so that when the database is created, the correct tables are added
from app.models.user import User
from app.models.task import Task
from app.models.subtask import Subtask
from app.schemas import TaskResponse
from app.models.moodleTask import MoodleTask
from app.models.reminders import Reminders
from app.models.notification import Notification
from app.scheduler import start_scheduler, stop_scheduler

from app.tasks import router as tasks_router
from app.reminders import router as reminders_router
from app.moodleTasks import router as moodletasks_router

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
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(reminders_router, prefix="/reminders", tags=["reminders"])
app.include_router(moodletasks_router, prefix="/moodletasks", tags=["moodletasks"])
class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str  # The title of the task
    description: Optional[str] = None  # A short description of the task
    completed: bool  # Whether or not the task is complete
    importance: int  # How important the task is (scale from 1-10)
    length: int  # How many minuites this will take (<5 - 300)
    tags: List[str] = (
        []
    )  # A list of string tags (can be []). No longer than 50 chars per tag
    due_at: Optional[datetime] = None  # The date that this must be completed by
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@app.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Retrieve all tasks",
    description="Fetches a list of all tasks from the database, including their ID, title, description, and completion status.",
)
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks