from sqlalchemy import Column, Integer, String, Date, Enum, TIMESTAMP, Interval
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..database import Base


class TaskPreferenceEnum(PyEnum):
    shortest_first = "shortest_first"
    easiest_first = "easiest_first"
    importance_first = "importance_first"
    due_date_first = "due_date_first"


class TaskReminderMethodEnum(PyEnum):  # Only email is implemented currently
    email = "email"
    sms = "sms"
    push_notification = "push_notification"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    task_preference = Column(
        Enum(TaskPreferenceEnum, name="task_preference_enum"),
        default=TaskPreferenceEnum.importance_first,
    )
    from datetime import timedelta

    task_reminder_interval = Column(Interval, default=timedelta(days=1))
    task_reminder_method = Column(
        Enum(TaskReminderMethodEnum, name="task_reminder_method_enum"),
        default=TaskReminderMethodEnum.email,
    )
    email = Column(String(255), unique=True)
    phone_number = Column(String(20), unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    notifications = relationship("Notification", back_populates="user")
