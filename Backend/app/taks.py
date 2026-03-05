import time
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
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



class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    importance: int = 0
    length: int
    tags: List[str] = []
    due_at: datetime


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    importance: Optional[int] = None
    length: Optional[int] = None
    tags: Optional[List[str]] = None
    due_at: Optional[datetime] = None



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




#Read all tasks
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    for task in tasks:
        task.priority = scoreTask(task)  # required by TaskResponse
    return tasks


#Read one task
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.priority = scoreTask(task)  # required by TaskResponse
    return task


#Create task
@app.post("/tasks", response_model=TaskResponse)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(**task_in.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    new_task.priority = scoreTask(new_task)  # required by TaskResponse
    return new_task


#Update task
@app.put("/tasks/{task_id}", response_model=TaskResponse)
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
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}



#Read all subtasks
@app.get("/subtasks", response_model=List[SubtaskResponse])
def get_subtasks(db: Session = Depends(get_db)):
    return db.query(Subtask).all()


#Read one subtask
@app.get("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


#Create subtask
@app.post("/subtasks", response_model=SubtaskResponse)
def create_subtask(subtask_in: SubtaskCreate, db: Session = Depends(get_db)):
    new_subtask = Subtask(**subtask_in.model_dump())
    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)
    return new_subtask


#update subtask
@app.put("/subtasks/{subtask_id}", response_model=SubtaskResponse)
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
@app.delete("/subtasks/{subtask_id}")
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return {"message": "Subtask deleted successfully"}



@app.post("/tasks/task/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.completed:
        raise HTTPException(status_code=400, detail="Task is already completed")

    current_time = datetime.now(timezone.utc)

    task.completed = True
    task.completed_at = current_time

    for subtask in task.subtasks:
        subtask.completed = True
        subtask.completed_at = current_time

    db.commit()
    db.refresh(task)

    return {"message": "Task completed"}


@app.post("/tasks/subtask/{subtask_id}/complete")
def complete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    if subtask.completed:
        raise HTTPException(status_code=400, detail="Subtask is already completed")

    parent_task = subtask.task
    current_time = datetime.now(timezone.utc)

    subtask.completed = True
    subtask.completed_at = current_time

    if all(st.completed for st in parent_task.subtasks):
        parent_task.completed = True
        parent_task.completed_at = current_time

    db.commit()
    db.refresh(subtask)

    return {"message": "Subtask completed"}


@app.post("/tasks/task/{task_id}/reopen")
def reopen_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.completed:
        raise HTTPException(status_code=400, detail="Task already open")

    task.completed = False
    task.completed_at = None

    db.commit()
    db.refresh(task)

    return {"message": "Task reopened"}


@app.post("/tasks/subtask/{subtask_id}/reopen")
def reopen_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    if not subtask.completed:
        raise HTTPException(status_code=400, detail="Subtask already open")

    parent_task = subtask.task

    subtask.completed = False
    subtask.completed_at = None

    if parent_task.completed:
        parent_task.completed = False
        parent_task.completed_at = None

    db.commit()
    db.refresh(subtask)

    return {"message": "Subtask reopened"}



app.include_router(reminders_router, prefix="/reminders", tags=["reminders"])
app.include_router(moodletasks_router, prefix="/moodletasks", tags=["moodletasks"])
