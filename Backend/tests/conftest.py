import sys
from pathlib import Path
import os

# Set DATABASE_URL to in-memory SQLite BEFORE importing any app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

# Import all models so SQLAlchemy knows about all tables
from app.database import Base, engine
from app.models.user import User
from app.models.task import Task
from app.models.subtask import Subtask
from app.models.reminders import Reminders
from app.models.notification import Notification

# Add more models here if needed

Base.metadata.create_all(bind=engine)
