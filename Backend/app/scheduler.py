from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from .database import SessionLocal
from .models.notification import Notification
from .models.user import User, TaskReminderMethodEnum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os


def send_email(to_email, subject, body):
    """Send an email via Gmail"""
    load_dotenv()

    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("✗ Gmail credentials not configured in .env")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"✗ Email send failed: {str(e)}")
        return False


def check_and_send_notifications():
    """Check for due notifications and send them"""
    db = SessionLocal()
    try:
        # Find notifications that are due now and haven't been sent yet
        due_notifications = (
            db.query(Notification)
            .filter(
                Notification.scheduled_at <= datetime.now(),
                Notification.delivered == False,
            )
            .all()
        )

        for notification in due_notifications:
            user = db.query(User).filter(User.id == notification.user_id).first()

            if user and user.task_reminder_method:
                success = False
                if user.task_reminder_method == TaskReminderMethodEnum.email:
                    if user.email:
                        success = send_email(
                            to_email=user.email,
                            subject="Task Reminder",
                            body=notification.message,
                        )
                        if success:
                            print(f"✓ Notification sent to {user.email}")
                        else:
                            print(f"✗ Failed to send notification to {user.email}")
                    else:
                        print(f"⚠ No email address for User ID {notification.user_id}")
                elif user.task_reminder_method == TaskReminderMethodEnum.sms:
                    # TODO: Implement SMS sending
                    print(
                        f"⚠ SMS notification not implemented for User ID {notification.user_id}"
                    )
                elif (
                    user.task_reminder_method
                    == TaskReminderMethodEnum.push_notification
                ):
                    # TODO: Implement push notification sending
                    print(
                        f"⚠ Push notification not implemented for User ID {notification.user_id}"
                    )
                else:
                    print(
                        f"⚠ Unknown notification method '{user.task_reminder_method}' for User ID {notification.user_id}"
                    )

                if success:
                    notification.delivered = True
                    db.commit()
                else:
                    db.rollback()

    except Exception as e:
        print(f"Error in check_and_send_notifications: {str(e)}")
    finally:
        db.close()


# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    check_and_send_notifications,
    IntervalTrigger(seconds=60),  # Check every 60 seconds
    id="notification_job",
    name="Check and send notifications",
    replace_existing=True,
)


def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        scheduler.start()
        print("✓ Notification scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("✓ Notification scheduler stopped")
