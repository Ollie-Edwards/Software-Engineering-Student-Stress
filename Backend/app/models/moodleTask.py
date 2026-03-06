from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class MoodleTask(Base):
    __tablename__ = "moodletasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    course_name = Column(String(255), nullable=False)
    activity = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    reference_url = Column(String(255), nullable=False)

    approved = Column(Boolean, nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="moodletasks")
