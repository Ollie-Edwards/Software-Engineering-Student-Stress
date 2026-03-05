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
        Add a new reminder to the database.
        """
        reminder = Reminders(
            task_id=task_id, remind_at=remind_at, status=status, enabled=enabled
        )
        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)
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
