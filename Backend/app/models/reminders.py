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
from database import Base

class Reminders(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key = True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    
    status = Column(Boolean, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    remind_at = Column(TIMESTAMP, )
    
    task = relationship("Task", back_populates="reminders")