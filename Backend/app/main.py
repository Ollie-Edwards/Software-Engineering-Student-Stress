from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from database import Base, engine, get_db, DATABASE_URL
from models.user import User
from models.task import Task
from models.subtask import Subtask

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

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

# marking a task as complete
@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session=Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    current_time = datetime.now(timezone.utc)

    task.completed = True
    task.completed_at = current_time

    for subtask in task.subtasks:
        subtask.completed = True
        subtask.completed_at = current_time

    db.commit()
    db.refresh(task)
    
    return {"message": "Task completed"}

# marking a subtask as complete
@app.post("/subtasks/{subtask_id}/complete")
def complete_subtask(subtask_id: int, db: Session=Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    subtask.completed = True
    subtask.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(subtask)
    
    return {"message": "Subtask completed"}

# reopen a task
@app.post("/tasks/{task_id}/reopen")
def reopen_task(task_id: int, db: Session=Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    task.completed = False
    task.completed_at = None

    for subtask in task.subtasks:
        subtask.completed = False
        subtask.completed_at = None

    db.commit()
    db.refresh(task)

    return {"message": "Task reopened"}

# reopen a subtask
@app.post("/subtasks/{subtask_id}/reopen")
def reopen_subtask(subtask_id: int, db: Session=Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    subtask.completed = False
    subtask.completed_at = None

    db.commit()
    db.refresh(subtask)

    return {"message": "Subtask reopened"}