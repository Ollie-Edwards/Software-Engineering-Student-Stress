import sys
from pathlib import Path
import os

# Set DATABASE_URL to in-memory SQLite BEFORE importing any app modules
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))
