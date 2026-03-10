import sys
from pathlib import Path
import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Add the app directory to the Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)


# Ensure testing database is reset between tests
@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    # Override dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# Task and Subtask factories
from datetime import datetime, timezone
import pytest
from app.models.task import Task
from app.models.subtask import Subtask
from app.models.moodleTask import MoodleTask


@pytest.fixture
def task_factory():
    def create_task(
        user_id=1,
        title="Test Task",
        description="Test description",
        completed=False,
        importance=5,
        length=30,
        tags=None,
        due_at=None,
        reminder_enabled=False,
    ):
        if tags is None:
            tags = []

        if due_at is None:
            due_at = datetime.now()

        return Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=completed,
            importance=importance,
            length=length,
            tags=tags,
            due_at=due_at,
            reminder_enabled=reminder_enabled,
        )

    return create_task


@pytest.fixture
def subtask_factory():
    def create_subtask(task, title="Test Subtask", completed=False, order_index=1):

        subtask = Subtask(
            task_id=task.id,
            title=title,
            completed=completed,
            order_index=order_index,
        )

        return subtask

    return create_subtask


# moodletask factory
@pytest.fixture
def moodletask_factory():
    def create_moodletask(
        user_id=1,
        course_name="Test Course",
        activity="Week 2: Using Git",
        title="Test Title",
        reference_url="https://example.com",
        approved=None,
        approved_at=None,
    ):
        return MoodleTask(
            user_id=user_id,
            course_name=course_name,
            activity=activity,
            title=title,
            reference_url=reference_url,
            approved=approved,
            approved_at=approved_at,
        )

    return create_moodletask
