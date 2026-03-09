from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.models.subtask import Subtask
from app.priorityScoring import scoreTask
from app.schemas import TaskResponse, SubtaskResponse

router = APIRouter()


@router.get(
    "",
    response_model=List[TaskResponse],
    summary="Retrieve all tasks",
    description="Fetches a list of all tasks from the database, including their ID, title, description, and completion status.",
)
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()

    for task in tasks:
        task.priority = scoreTask(task)

    return tasks


# Marking a task as complete
@router.post("/task/{task_id}/complete")
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

    if task.completed:
        return {"message": "Task completed"}


# Marking a subtask as complete
@router.post("/subtask/{subtask_id}/complete")
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

    # If all subtasks of the parent task is complete, mark parent task as complete
    if all(st.completed for st in parent_task.subtasks):
        parent_task.completed = True
        parent_task.completed_at = current_time

    db.commit()
    db.refresh(subtask)

    if subtask.completed:
        return {"message": "Subtask completed"}


# Reopen a task
@router.post("/task/{task_id}/reopen")
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

    if not task.completed:
        return {"message": "Task reopened"}


# Reopen a subtask
@router.post("/subtask/{subtask_id}/reopen")
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

    if not subtask.completed:
        return {"message": "Subtask reopened"}


# ============================================================
#CRUD endpoints for tasks
# For responses, read endpoints return TaskResponse.
# Create/update accept JSON bodies directly using Body(...),
# ============================================================


# Read one task
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Add computed priority so the returned object matches TaskResponse
    task.priority = scoreTask(task)
    return task


# Create a new task
@router.post("", response_model=TaskResponse)
def create_task(
    task_data: dict = Body(...), db: Session = Depends(get_db)
):  # Body(...) accepts JSON request, **task_data unpacks it into the correct format
    # Create a new Task database object from the request body
    new_task = Task(**task_data)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Add computed priority before returning it
    new_task.priority = scoreTask(new_task)
    return new_task


# Update an existing task
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, task_data: dict = Body(...), db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only the fields that were sent in the request body
    for field, value in task_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    # Add computed priority before returning it
    task.priority = scoreTask(task)
    return task


# Delete a task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


# ============================================================
# CRUD endpoints for subtasks
# Read endpoints return SubtaskResponse.
# Create/update accept JSON bodies directly using Body(...),
# ============================================================


# Read all subtasks
@router.get("/subtasks", response_model=List[SubtaskResponse])
def get_all_subtasks(db: Session = Depends(get_db)):
    subtasks = db.query(Subtask).all()
    return subtasks


# Read one subtask
@router.get("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    return subtask


# Create a new subtask
@router.post("/subtasks", response_model=SubtaskResponse)
def create_subtask(subtask_data: dict = Body(...), db: Session = Depends(get_db)):
    # Create a new Subtask database object from the request body
    new_subtask = Subtask(**subtask_data)

    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)

    return new_subtask


# Update an existing subtask
@router.put("/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    subtask_id: int, subtask_data: dict = Body(...), db: Session = Depends(get_db)
):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    # Update only the fields that were sent in the request body
    for field, value in subtask_data.items():
        setattr(subtask, field, value)

    db.commit()
    db.refresh(subtask)

    return subtask


# Delete a subtask
@router.delete("/subtasks/{subtask_id}")
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()

    return {"message": "Subtask deleted successfully"}
