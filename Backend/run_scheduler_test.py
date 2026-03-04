from datetime import datetime
import time

from app.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification

import app.scheduler as scheduler


def setup_test_data(db):
    # create a test user
    user = User(
        name="Test User",
        date_of_birth=datetime(2000, 1, 1).date(),
        email="tj.test.email44@gmail.com",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # create a notification due now
    notif = Notification(
        user_id=user.id,
        message="[TEST] This is a test notification",
        scheduled_at=datetime.now(),
        delivered=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return user, notif


def cleanup_test_data(db, user, notif):
    try:
        db.delete(notif)
        db.delete(user)
        db.commit()
    except Exception:
        db.rollback()


def main():
    db = SessionLocal()
    user = None
    notif = None
    try:
        user, notif = setup_test_data(db)

        # Stub out actual email sending so we can test behaviour without SMTP
        # scheduler.send_email = lambda to_email, subject, body: True

        print("Before: delivered=", notif.delivered)

        # run the scheduler check function directly
        scheduler.check_and_send_notifications()

        # give DB a moment and reload
        time.sleep(1)
        db.refresh(notif)
        print("After: delivered=", notif.delivered)

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if db is not None:
            if notif is not None:
                try:
                    db.delete(notif)
                except Exception:
                    db.rollback()
            if user is not None:
                try:
                    db.delete(user)
                except Exception:
                    db.rollback()
            try:
                db.commit()
            except Exception:
                db.rollback()
            db.close()


if __name__ == "__main__":
    main()
