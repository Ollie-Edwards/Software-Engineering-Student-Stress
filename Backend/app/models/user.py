from sqlalchemy import Column, Integer, String, Date, Enum, TIMESTAMP
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base


class TaskPreferenceEnum(PyEnum):
    shortest_first = "shortest_first"
    easiest_first = "easiest_first"
    importance_first = "importance_first"
    due_date_first = "due_date_first"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    task_preference = Column(
        Enum(TaskPreferenceEnum, name="task_preference_enum"),
        default=TaskPreferenceEnum.importance_first,
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
