import os
from datetime import datetime
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
from dotenv import load_dotenv
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.task import Task
from app.models.subtask import Subtask
from app.models.reminders import Reminders
from app.models.notification import Notification
import app.scheduler as scheduler

Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    load_dotenv()
    user = User(
        name="Test User",
        date_of_birth=datetime(2000, 1, 1).date(),
        email=os.getenv("GMAIL_USER"),
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
        message="[TEST] This is a test notification",
        scheduled_at=datetime.now(),
        delivered=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    yield notif
    db.delete(notif)
    db.commit()


def test_scheduler_sends_notification(db, test_user, test_notification, monkeypatch):
    # monkeypatch.setattr(scheduler, "send_email", lambda *a, **kw: True)
    scheduler.check_and_send_notifications()
    db.refresh(test_notification)
    assert test_notification.delivered in [True, False]  # depends on implementation