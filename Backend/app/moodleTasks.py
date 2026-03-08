from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.moodleTask import MoodleTask
from app.models.task import Task

router = APIRouter()


@router.get("")  # default /moodletasks endpoint
def get_tasks(db: Session = Depends(get_db)):
    moodleTasks = (
        db.query(MoodleTask).filter(MoodleTask.user_id == 2).all()
    )  # Hard coded user 2, until users are implemented

    if not moodleTasks:
        raise HTTPException(status_code=404, detail="No Tasks Found")

    else:
        return moodleTasks

@router.get("")  # default /moodletasks endpoint
def get_tasks(db: Session = Depends(get_db)):
    moodleTasks = (
        db.query(MoodleTask).filter(MoodleTask.user_id == 2).all()
    )  # Hard coded user 2, until users are implemented

    if not moodleTasks:
        raise HTTPException(status_code=404, detail="No Tasks Found")

    else:
        return moodleTasks

@router.post("/{task_id}/approve")
def approve_task(task_id: int, db: Session = Depends(get_db)):
    moodleTask = (db.query(MoodleTask)
                    .filter(MoodleTask.id == task_id, MoodleTask.user_id == 2)
                    .first()
                )

    if not moodleTask:
        raise HTTPException(status_code=404, detail="Task Not Found")

    if moodleTask.approved:
        raise HTTPException(status_code=400, detail="Task already approved")

    new_task = Task(
        user_id=moodleTask.user_id,
        title=moodleTask.title,
        description=f"{moodleTask.course_name} | {moodleTask.activity}",
        length=20,
        importance=5,
        due_at=moodleTask.due_at if moodleTask.due_at else datetime.now() + timedelta(days=1),
        reference_url=moodleTask.reference_url
    )

    moodleTask.approved = True
    moodleTask.approved_at = datetime.now()

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"detail": "Task approved", "task_id": new_task.id}

@router.delete("/{task_id}/reject")
def reject_task(task_id: int, db: Session = Depends(get_db)):
    moodleTask = (db.query(MoodleTask)
                    .filter(MoodleTask.id == task_id, MoodleTask.user_id == 2)
                    .first()
                 )

    if not moodleTask:
        raise HTTPException(status_code=404, detail="Task Not Found")

    moodleTask.approved = False
    db.commit()

    return {"detail": "Task rejected"}
