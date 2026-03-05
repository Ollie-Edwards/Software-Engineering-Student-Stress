from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.moodleTask import MoodleTask
from app.schemas import TaskResponse
from app.moodleService import MoodleService

router = APIRouter()


@router.get("")  # default /moodletasks endpoint
def get_tasks(db: Session = Depends(get_db)):
    user_id = 2 # Hard coded user 2, until users are implemented

    moodle_tasks = MoodleService.get_tasks(db, user_id)

    if not moodle_tasks:
        raise HTTPException(status_code=404, detail="No Tasks Found")
    else:
        return moodle_tasks
    
@router.get("/pending")
def get_pending_tasks(db: Session = Depends(get_db)):
    user_id = 2
    pending_tasks = MoodleService.get_pending_tasks(db, user_id)

    if not pending_tasks:
        raise HTTPException(status_code=404, detail="No Tasks Found")
    else:
        return pending_tasks

@router.post("/sync")
def sync_tasks(db: Session = Depends(get_db)):
    user_id = 2
    tasks = MoodleService.sync_tasks(db, user_id)

    return {"tasks_created": len(tasks)}
    
@router.post("/{task_id}/approve")
def approve_task(task_id: int, db: Session = Depends(get_db)):
    task = MoodleService.approve_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="No Task Found")
    
    if task == "already modified":
        raise HTTPException(status_code=400, detail="Task has already been approved/rejected")
    
    return {"message": "Task approved"}

@router.post("/{task_id}/reject")
def reject_task(task_id: int, db: Session = Depends(get_db)):
    task = MoodleService.reject_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="No Task Found")
    
    if task == "already modified":
        raise HTTPException(status_code=400, detail="Task has already been approved/rejected")

    return {"message": "Task rejected"}