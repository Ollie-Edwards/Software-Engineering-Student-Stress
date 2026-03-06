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

def test_enable_reminders_success(client, db, task_factory):
    task = task_factory(reminder_enabled=False)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/enable_reminders")

    assert response.status_code == 200
    assert response.json() == {"message": "Task reminder enabled"}

    db.refresh(task)
    assert task.reminder_enabled is True


def test_enable_reminders_already_enabled(client, db, task_factory):
    task = task_factory(reminder_enabled=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/enable_reminders")

    assert response.status_code == 400
    assert response.json() == {"detail": "Reminders already enabled"}


def test_enable_reminders_missing_task(client):
    response = client.post("/reminders/234/enable_reminders")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_disable_reminders_success(client, db, task_factory):
    task = task_factory(reminder_enabled=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/disable_reminders")

    assert response.status_code == 200
    assert response.json() == {"message": "Task reminder disabled"}

    db.refresh(task)
    assert task.reminder_enabled is False


def test_disable_reminders_already_disabled(client, db, task_factory):
    task = task_factory(reminder_enabled=False)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/disable_reminders")

    assert response.status_code == 400
    assert response.json() == {"detail": "Task reminders already disabled"}


def test_disable_reminders_missing_task(client):
    response = client.post("/reminders/234/disable_reminders")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
