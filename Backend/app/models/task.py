from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    SmallInteger,
    TIMESTAMP,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, nullable=False, default=False)
    importance = Column(SmallInteger, default=0)
    length = Column(Integer)
    tags = Column(JSON)
    due_at = Column(TIMESTAMP)
    reference_url = Column(String(255), nullable=True)
    reminder_enabled = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", backref="tasks")
    subtasks = relationship("Subtask", back_populates="task")
