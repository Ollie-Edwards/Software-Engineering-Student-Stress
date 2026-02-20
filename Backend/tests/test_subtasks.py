from datetime import date
from fastapi.testclient import TestClient

import main
from database import Base, engine, SessionLocal
from models.user import User, TaskPreferenceEnum
from models.task import Task

client = TestClient(main.app)


def setup_function():
    # Fresh DB each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def seed_user_and_task():
    db = SessionLocal()
    try:
        user = User(
            name="Test User",
            date_of_birth=date(2000, 1, 1),
            task_preference=TaskPreferenceEnum.importance_first,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        task = Task(
            user_id=user.id,
            title="Test Task",
            description="desc",
            completed=False,
            importance=5,
            length=30,
            tags=0,
            due_at=None,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        return user.id, task.id
    finally:
        db.close()


def test_create_and_get_subtask():
    _, task_id = seed_user_and_task()

    # CREATE
    r = client.post(
        f"/tasks/{task_id}/subtasks",
        json={"title": "Subtask A", "status": False, "order_index": 1},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["task_id"] == task_id
    assert data["title"] == "Subtask A"

    subtask_id = data["id"]

    # READ single
    r2 = client.get(f"/subtasks/{subtask_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == subtask_id


def test_list_subtasks_for_task():
    _, task_id = seed_user_and_task()

    client.post(
        f"/tasks/{task_id}/subtasks",
        json={"title": "S1", "status": False, "order_index": 2},
    )
    client.post(
        f"/tasks/{task_id}/subtasks",
        json={"title": "S0", "status": True, "order_index": 1},
    )

    r = client.get(f"/tasks/{task_id}/subtasks")
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 2


def test_update_subtask():
    _, task_id = seed_user_and_task()

    r = client.post(
        f"/tasks/{task_id}/subtasks",
        json={"title": "Old", "status": False},
    )
    subtask_id = r.json()["id"]

    r2 = client.put(
        f"/subtasks/{subtask_id}",
        json={"title": "New", "status": True, "order_index": 7},
    )
    assert r2.status_code == 200
    assert r2.json()["title"] == "New"


def test_delete_subtask():
    _, task_id = seed_user_and_task()

    r = client.post(
        f"/tasks/{task_id}/subtasks",
        json={"title": "To delete", "status": False},
    )
    subtask_id = r.json()["id"]

    r2 = client.delete(f"/subtasks/{subtask_id}")
    assert r2.status_code == 204

    r3 = client.get(f"/subtasks/{subtask_id}")
    assert r3.status_code == 404