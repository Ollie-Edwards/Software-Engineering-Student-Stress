import time

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.database import Base, engine, get_db, DATABASE_URL

# These are required so that when the database is created, the correct tables are added
from app.models.user import User
from app.models.task import Task
from app.models.subtask import Subtask
from app.schemas import TaskResponse
from app.models.moodleTask import MoodleTask

from app.tasks import router as tasks_router
from app.reminders import router as reminders_router
from app.moodleTasks import router as moodletasks_router

engine = create_engine(DATABASE_URL)
while True:
    try:
        conn = engine.connect()
        conn.close()
        break
    except OperationalError:
        print("Database not ready, retrying in 2s...")
        time.sleep(2)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(reminders_router, prefix="/reminders", tags=["reminders"])
app.include_router(moodletasks_router, prefix="/moodletasks", tags=["moodletasks"])
