from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.moodleTask import MoodleTask
from app.schemas import TaskResponse

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
