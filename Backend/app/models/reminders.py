from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    SmallInteger,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
import os


class Reminders(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )

    status = Column(Boolean, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    remind_at = Column(
        TIMESTAMP,
    )

    task = relationship("Task", back_populates="reminders")

    @staticmethod
    def add_reminder(db_session, task_id, remind_at=None, status=True, enabled=True):
        """
        Add a new reminder to the database and send notification instantly.
        """
        reminder = Reminders(
            task_id=task_id, remind_at=remind_at, status=status, enabled=enabled
        )
        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)

        # --- Send notification instantly ---
        from app.models.notification import Notification
        from app.models.task import Task
        from app.models.user import User
        from app.scheduler import send_email
        from datetime import datetime

        # Get task and user
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return reminder
        user = db_session.query(User).filter(User.id == task.user_id).first()
        if not user:
            return reminder

        # Compose notification message
        msg_line = f"- {task.title} (due {task.due_at.strftime('%Y-%m-%d %H:%M') if task.due_at else 'N/A'})"
        scheduled_at = remind_at if remind_at else datetime.now()

        notification = Notification(
            user_id=user.id,
            message=msg_line,
            scheduled_at=scheduled_at,
            delivered=False,
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)

        # Send email instantly if user has email and prefers email
        if (
            hasattr(user, "task_reminder_method")
            and getattr(user.task_reminder_method, "name", None) == "email"
            and user.email
        ):
            print(
                f"[DEBUG] About to send email to {user.email} with subject 'Task Reminder' and body: {msg_line}"
            )
            send_email(
                to_email=user.email,
                subject="Task Reminder",
                body=msg_line,
            )
            print(f"[DEBUG] send_email called for {user.email}")

        return reminder

    @staticmethod
    def edit_reminder(db_session, reminder_id, **kwargs):
        """
        Edit an existing reminder. kwargs can include: task_id, remind_at, status, enabled
        """
        reminder = (
            db_session.query(Reminders).filter(Reminders.id == reminder_id).first()
        )
        if not reminder:
            return None
        for key, value in kwargs.items():
            if hasattr(reminder, key):
                setattr(reminder, key, value)
        db_session.commit()
        db_session.refresh(reminder)
        return reminder

    @staticmethod
    def delete_reminder(db_session, reminder_id):
        """
        Delete a reminder by its ID.
        """
        reminder = (
            db_session.query(Reminders).filter(Reminders.id == reminder_id).first()
        )
        if not reminder:
            return False
        db_session.delete(reminder)
        db_session.commit()
        return True
