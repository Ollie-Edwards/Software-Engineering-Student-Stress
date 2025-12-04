from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False)
    order_index = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    task = relationship("Task", back_populates="subtasks")
