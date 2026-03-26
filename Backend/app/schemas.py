from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: str = None
    importance: int = 0
    length: int = 0
    tags: List[str] = []
    due_at: datetime
    reminder_enabled: bool = False

class SubtaskResponse(BaseModel):
    id: int
    task_id: int
    title: str
    order_index: int | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

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
    due_at: datetime  # The date that this must be completed by
    reference_url: Optional[str] = None
    priority: float  # Determines the task priority score
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = []

    model_config = ConfigDict(from_attributes=True)

