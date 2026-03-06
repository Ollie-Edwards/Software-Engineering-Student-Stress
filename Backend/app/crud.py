import time
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.database import Base, get_db, DATABASE_URL
from app.models.task import Task
from app.models.subtask import Subtask
from app.priorityScoring import scoreTask
from app.schemas import TaskResponse

from app.reminders import router as reminders_router
from app.moodleTasks import router as moodletasks_router

router = APIRouter()

#Read all tasks
@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    for task in tasks:
        task.priority = scoreTask(task)  # required by TaskResponse
    return tasks


#Read one task
@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.priority = scoreTask(task)  # required by TaskResponse
    return task


#Create task
@router.post("/tasks")
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(**task_in.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    new_task.priority = scoreTask(new_task)  # required by TaskResponse
    return new_task


#Update task
@router.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    task.priority = scoreTask(task)  # required by TaskResponse
    return task


#Delete task
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}



#Read all subtasks
@router.get("/subtasks")
def get_subtasks(db: Session = Depends(get_db)):
    return db.query(Subtask).all()


#Read one subtask
@router.get("/subtasks/{subtask_id}")
def get_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


#Create subtask
@router.post("/subtasks")
def create_subtask(subtask_in: SubtaskCreate, db: Session = Depends(get_db)):
    new_subtask = Subtask(**subtask_in.model_dump())
    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)
    return new_subtask


#update subtask
@router.put("/subtasks/{subtask_id}")
def update_subtask(
    subtask_id: int, subtask_update: SubtaskUpdate, db: Session = Depends(get_db)
):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    update_data = subtask_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subtask, key, value)

    db.commit()
    db.refresh(subtask)
    return subtask


#Delete subtask
@router.delete("/subtasks/{subtask_id}")
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return {"message": "Subtask deleted successfully"}
