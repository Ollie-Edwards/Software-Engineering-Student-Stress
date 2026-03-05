from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from database import Base, get_db, DATABASE_URL
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
    title: str
    description: Optional[str] = None
    completed: bool
    importance: int
    length: Optional[int] = None
    tags: List[str] = []
    due_at: Optional[datetime] = None
    reminder_enabled: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    importance: int = 0
    length: Optional[int] = None
    tags: List[str] = []
    due_at: Optional[datetime] = None
    reminder_enabled: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    importance: Optional[int] = None
    length: Optional[int] = None
    tags: Optional[List[str]] = None
    due_at: Optional[datetime] = None
    reminder_enabled: Optional[bool] = None
    completed_at: Optional[datetime] = None


# task CRUD


@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(**task.model_dump())

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


class SubtaskResponse(BaseModel):
    id: int
    task_id: int
    title: str
    status: bool
    order_index: Optional[int] = None
    completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SubtaskCreate(BaseModel):
    task_id: int
    title: str
    status: bool
    completed: bool
    order_index: Optional[int] = None


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[bool] = None
    completed: Optional[bool] = None
    order_index: Optional[int] = None
    completed_at: Optional[datetime] = None


# subtask CRUD


@app.get("/subtasks", response_model=List[SubtaskResponse])
def get_subtasks(db: Session = Depends(get_db)):
    return db.query(Subtask).all()


@app.get("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(subtask_id: int, db: Session = Depends(get_db)):

    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    return subtask


@app.post("/subtasks", response_model=SubtaskResponse)
def create_subtask(subtask: SubtaskCreate, db: Session = Depends(get_db)):

    new_subtask = Subtask(**subtask.model_dump())

    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)

    return new_subtask


@app.put("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    subtask_id: int,
    subtask_update: SubtaskUpdate,
    db: Session = Depends(get_db),
):

    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    update_data = subtask_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(subtask, key, value)

    db.commit()
    db.refresh(subtask)

    return subtask


@app.delete("/subtasks/{subtask_id}")
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):

    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()

    return {"message": "Subtask deleted successfully"}
