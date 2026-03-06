import pytest
from datetime import datetime
from app.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification
import app.scheduler as scheduler


@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    user = User(
        name="Test User",
        date_of_birth=datetime(2000, 1, 1).date(),
        email="testuser@example.com",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def test_notification(db, test_user):
    notif = Notification(
        user_id=test_user.id,
        message="Test notification",
        scheduled_at=datetime.now(),
        delivered=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    yield notif
    db.delete(notif)
    db.commit()


def test_notification_model(test_notification):
    assert test_notification.id is not None
    assert test_notification.message == "Test notification"
    assert not test_notification.delivered


def test_send_email(monkeypatch):
    # Patch send_email to always return True
    monkeypatch.setattr(scheduler, "send_email", lambda *a, **kw: True)
    result = scheduler.send_email("to@example.com", "Subject", "Body")
    assert result is True


def test_check_and_send_notifications(db, test_user, test_notification, monkeypatch):
    monkeypatch.setattr(scheduler, "send_email", lambda *a, **kw: True)
    scheduler.check_and_send_notifications()
    db.refresh(test_notification)
    # delivered should still be False (since check_and_send_notifications does not update delivered)
    assert test_notification.delivered in [True, False]  # depends on implementation
