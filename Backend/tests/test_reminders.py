import pytest
from datetime import datetime
from app.database import SessionLocal
from app.models.reminders import Reminders


@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_reminder(db):
    reminder = Reminders(
        task_id=1,
        status=False,
        enabled=True,
        remind_at=datetime.now(),
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    yield reminder
    db.delete(reminder)
    db.commit()


def test_reminder_model(test_reminder):
    assert test_reminder.id is not None
    assert test_reminder.enabled is True
    assert test_reminder.status is False
    assert test_reminder.remind_at is not None
