import time

from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

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

app.include_router(tasks_router)
app.include_router(reminders_router)


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


# ----------------- SUBSTACK CRUD ------------------------------------------------------------------------

class SubtaskCreate(BaseModel):
    title: str
    status: bool = False
    order_index: Optional[int] = None


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[bool] = None
    order_index: Optional[int] = None


class SubtaskResponse(BaseModel):
    id: int
    task_id: int
    title: str
    status: bool
    order_index: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@app.get("/tasks/{task_id}/subtasks", response_model=List[SubtaskResponse])
def list_subtasks(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return (
        db.query(Subtask)
        .filter(Subtask.task_id == task_id)
        .order_by(Subtask.order_index.is_(None), Subtask.order_index, Subtask.id)
        .all()
    )


@app.post(
    "/tasks/{task_id}/subtasks",
    response_model=SubtaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subtask(task_id: int, payload: SubtaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    subtask = Subtask(
        task_id=task_id,
        title=payload.title,
        status=payload.status,
        order_index=payload.order_index,
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask


@app.get("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


@app.put("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(subtask_id: int, payload: SubtaskUpdate, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    if payload.title is not None:
        subtask.title = payload.title
    if payload.status is not None:
        subtask.status = payload.status
    if payload.order_index is not None:
        subtask.order_index = payload.order_index

    db.commit()
    db.refresh(subtask)
    return subtask


@app.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return None