from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task

router = APIRouter()


# Enable Reminders
@router.post("/{task_id}/enable_reminders")
def enable_reminders(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.reminder_enabled:
        raise HTTPException(status_code=400, detail="Reminders already enabled")

    task.reminder_enabled = True

    db.commit()
    db.refresh(task)

    if task.reminder_enabled:
        return {"message": "Task reminder enabled"}


# Disable Reminders
@router.post("/{task_id}/disable_reminders")
def disable_reminders(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.reminder_enabled:
        raise HTTPException(status_code=400, detail="Task reminders already disabled")

    task.reminder_enabled = False

    db.commit()
    db.refresh(task)

    if not task.reminder_enabled:
        return {"message": "Task reminder disabled"}
