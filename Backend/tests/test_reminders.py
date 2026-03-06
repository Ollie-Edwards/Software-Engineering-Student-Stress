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


def test_add_reminder(db):
    remind_at = datetime.now()
    reminder = Reminders.add_reminder(
        db, task_id=1, remind_at=remind_at, status=True, enabled=True
    )
    assert reminder.id is not None
    assert reminder.task_id == 1
    assert reminder.status is True
    assert reminder.enabled is True
    assert reminder.remind_at == remind_at
    # Clean up
    db.delete(reminder)
    db.commit()


def test_edit_reminder(db):
    remind_at = datetime.now()
    reminder = Reminders.add_reminder(
        db, task_id=1, remind_at=remind_at, status=True, enabled=True
    )
    new_remind_at = datetime.now()
    updated = Reminders.edit_reminder(
        db, reminder.id, status=False, enabled=False, remind_at=new_remind_at
    )
    assert updated.status is False
    assert updated.enabled is False
    assert updated.remind_at == new_remind_at
    # Clean up
    db.delete(reminder)
    db.commit()


def test_delete_reminder(db):
    remind_at = datetime.now()
    reminder = Reminders.add_reminder(
        db, task_id=1, remind_at=remind_at, status=True, enabled=True
    )
    deleted = Reminders.delete_reminder(db, reminder.id)
    assert deleted is True
    # Ensure it's gone
    result = db.query(Reminders).filter(Reminders.id == reminder.id).first()
    assert result is None
