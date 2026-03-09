from datetime import datetime, timezone

from app.models.task import Task
from app.models.subtask import Subtask

# GET "/tasks/"


def test_retreive_tasks(client, db, task_factory):
    # Create test data
    task1 = task_factory(title="Task 1")
    task2 = task_factory(title="Task 2")

    db.add_all([task1, task2])
    db.commit()

    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    # Should be a list
    assert isinstance(data, list)

    # Should contain at least 2 tasks
    assert len(data) >= 2

    first_task = data[0]

    assert "id" in first_task
    assert "title" in first_task
    assert "description" in first_task
    assert "completed" in first_task


# POST "/tasks/{task_id}/complete"


def test_standard_complete_task(client, db, task_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/tasks/task/{task.id}/complete")
    assert response.status_code == 200
    assert response.json() == {"message": "Task completed"}


def test_double_complete_task(client, db, task_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/tasks/task/{task.id}/complete")
    assert response.status_code == 200
    assert response.json() == {"message": "Task completed"}

    # try to complete the same task again
    response = client.post(f"/tasks/task/{task.id}/complete")
    assert response.status_code == 400
    assert response.json() == {"detail": "Task is already completed"}


def test_complete_missing_task(client):
    response = client.post(f"/tasks/task/234/complete")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_subtasks_are_completed_on_task_completion(
    client, db, task_factory, subtask_factory
):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    # Create subtasks
    subtask1 = subtask_factory(task, title="Subtask 1", order_index=1, completed=False)
    subtask2 = subtask_factory(task, title="Subtask 2", order_index=1, completed=True)

    db.add_all([subtask1, subtask2])
    db.commit()

    response = client.post(f"/tasks/task/{task.id}/complete")

    assert response.status_code == 200
    assert response.json() == {"message": "Task completed"}

    db.refresh(task)

    for subtask in task.subtasks:
        assert subtask.completed is True


# POST "/subtasks/{subtask_id}/complete"


def test_standard_complete_subtask(client, db, task_factory, subtask_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="Subtask 1", order_index=1, completed=False)

    db.add(subtask)
    db.commit()

    response = client.post(f"/tasks/subtask/{subtask.id}/complete")
    assert response.status_code == 200
    assert response.json() == {"message": "Subtask completed"}


def test_double_complete_subtask(client, db, task_factory, subtask_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="Subtask 1", order_index=1, completed=False)

    db.add(subtask)
    db.commit()

    response = client.post(f"/tasks/subtask/{subtask.id}/complete")
    assert response.status_code == 200
    assert response.json() == {"message": "Subtask completed"}

    response = client.post(f"/tasks/subtask/{subtask.id}/complete")
    assert response.status_code == 400
    assert response.json() == {"detail": "Subtask is already completed"}


def test_complete_missing_subtask(client):
    response = client.post(f"/tasks/subtask/234/complete")
    assert response.status_code == 404
    assert response.json() == {"detail": "Subtask not found"}


# POST /tasks/{task_id}/reopen


def test_standard_reopen_task(client, db, task_factory):
    task = task_factory(completed=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/tasks/task/{task.id}/reopen")
    assert response.status_code == 200
    assert response.json() == {"message": "Task reopened"}


def test_double_reopen_task(client, db, task_factory):
    task = task_factory(completed=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/tasks/task/{task.id}/reopen")
    assert response.status_code == 200
    assert response.json() == {"message": "Task reopened"}

    response = client.post(f"/tasks/task/{task.id}/reopen")
    assert response.status_code == 400
    assert response.json() == {"detail": "Task already open"}


def test_reopen_missing_task(client):
    response = client.post(f"/tasks/task/234/reopen")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


# POST /subtasks/{subtask_id}/reopen


def test_standard_reopen_task(client, db, task_factory, subtask_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="Subtask 1", order_index=1, completed=True)

    db.add(subtask)
    db.commit()

    response = client.post(f"/tasks/subtask/{subtask.id}/reopen")
    assert response.status_code == 200
    assert response.json() == {"message": "Subtask reopened"}


def test_double_reopen_subtask(client, db, task_factory, subtask_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="Subtask 1", order_index=1, completed=True)

    db.add(subtask)
    db.commit()

    response = client.post(f"/tasks/subtask/{subtask.id}/reopen")
    assert response.status_code == 200
    assert response.json() == {"message": "Subtask reopened"}

    response = client.post(f"/tasks/subtask/{subtask.id}/reopen")
    assert response.status_code == 400
    assert response.json() == {"detail": "Subtask already open"}


def test_reopen_missing_subtask(client):
    response = client.post(f"/tasks/subtask/234/reopen")
    assert response.status_code == 404
    assert response.json() == {"detail": "Subtask not found"}


def test_reopen_subtask_reopens_parent_task(client, db, task_factory, subtask_factory):
    task = task_factory(completed=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, completed=True)

    db.add(subtask)
    db.commit()
    db.refresh(subtask)

    # Make sure they start completed
    assert task.completed is True
    assert subtask.completed is True

    response = client.post(f"/tasks/subtask/{subtask.id}/reopen")

    assert response.status_code == 200
    assert response.json() == {"message": "Subtask reopened"}

    db.refresh(task)
    db.refresh(subtask)

    assert subtask.completed is False
    assert task.completed is False

#==============================================
#Testing CRUD
#==============================================

# ==============================================
# Testing CRUD
# ==============================================


def _create_test_user(db):
    from datetime import date
    from app.models.user import User

    user = User(name="Test User", date_of_birth=date(2000, 1, 1))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# GET "/tasks/{task_id}"


def test_get_single_task(client, db, task_factory):
    task = task_factory(title="Single Task")

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.get(f"/tasks/{task.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == "Single Task"
    assert "priority" in data


def test_get_missing_task(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


# POST "/tasks"


def test_create_task(client, db):
    user = _create_test_user(db)

    payload = {
        "user_id": user.id,
        "title": "Created Task",
        "description": "Created from test",
        "completed": False,
        "importance": 7,
        "length": 60,
        "tags": ["test", "crud"],
        "due_at": None,
        "reminder_enabled": False,
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Created Task"
    assert data["description"] == "Created from test"
    assert data["importance"] == 7
    assert data["length"] == 60
    assert data["tags"] == ["test", "crud"]
    assert "id" in data
    assert "priority" in data

    created_task = db.query(Task).filter(Task.id == data["id"]).first()
    assert created_task is not None
    assert created_task.title == "Created Task"


# PUT "/tasks/{task_id}"


def test_update_task(client, db, task_factory):
    task = task_factory(title="Old Title", importance=3, length=30)

    db.add(task)
    db.commit()
    db.refresh(task)

    payload = {
        "title": "Updated Title",
        "importance": 9,
        "length": 120,
    }

    response = client.put(f"/tasks/{task.id}", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == "Updated Title"
    assert data["importance"] == 9
    assert data["length"] == 120

    db.refresh(task)
    assert task.title == "Updated Title"
    assert task.importance == 9
    assert task.length == 120


def test_update_missing_task(client):
    payload = {"title": "Does not exist"}

    response = client.put("/tasks/9999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


# DELETE "/tasks/{task_id}"


def test_delete_task(client, db, task_factory):
    task = task_factory(title="Delete Me")

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}

    deleted_task = db.query(Task).filter(Task.id == task.id).first()
    assert deleted_task is None


def test_delete_missing_task(client):
    response = client.delete("/tasks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


# GET "/tasks/subtasks"


def test_get_all_subtasks(client, db, task_factory, subtask_factory):
    task = task_factory()
    db.add(task)
    db.commit()
    db.refresh(task)

    subtask1 = subtask_factory(task, title="Subtask 1", order_index=1)
    subtask2 = subtask_factory(task, title="Subtask 2", order_index=2)

    db.add_all([subtask1, subtask2])
    db.commit()

    response = client.get("/tasks/subtasks")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    first_subtask = data[0]
    assert "id" in first_subtask
    assert "task_id" in first_subtask
    assert "title" in first_subtask
    assert "completed" in first_subtask
    assert "order_index" in first_subtask


# GET "/tasks/subtasks/{subtask_id}"


def test_get_single_subtask(client, db, task_factory, subtask_factory):
    task = task_factory()
    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="One Subtask", order_index=1)

    db.add(subtask)
    db.commit()
    db.refresh(subtask)

    response = client.get(f"/tasks/subtasks/{subtask.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == subtask.id
    assert data["task_id"] == task.id
    assert data["title"] == "One Subtask"


def test_get_missing_subtask(client):
    response = client.get("/tasks/subtasks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Subtask not found"}


# POST "/tasks/subtasks"


def test_create_subtask(client, db, task_factory):
    task = task_factory()
    db.add(task)
    db.commit()
    db.refresh(task)

    payload = {
        "task_id": task.id,
        "title": "Created Subtask",
        "completed": False,
        "order_index": 1,
    }

    response = client.post("/tasks/subtasks", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["task_id"] == task.id
    assert data["title"] == "Created Subtask"
    assert data["completed"] is False
    assert data["order_index"] == 1
    assert "id" in data

    created_subtask = db.query(Subtask).filter(Subtask.id == data["id"]).first()
    assert created_subtask is not None
    assert created_subtask.title == "Created Subtask"


# PUT "/tasks/subtasks/{subtask_id}"


def test_update_subtask(client, db, task_factory, subtask_factory):
    task = task_factory()
    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="Old Subtask", order_index=1)
    db.add(subtask)
    db.commit()
    db.refresh(subtask)

    payload = {
        "title": "Updated Subtask",
        "completed": True,
        "order_index": 2,
    }

    response = client.put(f"/tasks/subtasks/{subtask.id}", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == subtask.id
    assert data["title"] == "Updated Subtask"
    assert data["completed"] is True
    assert data["order_index"] == 2

    db.refresh(subtask)
    assert subtask.title == "Updated Subtask"
    assert subtask.completed is True
    assert subtask.order_index == 2


def test_update_missing_subtask(client):
    payload = {"title": "Does not exist"}

    response = client.put("/tasks/subtasks/9999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Subtask not found"}


# DELETE "/tasks/subtasks/{subtask_id}"


def test_delete_subtask(client, db, task_factory, subtask_factory):
    task = task_factory()
    db.add(task)
    db.commit()
    db.refresh(task)

    subtask = subtask_factory(task, title="Delete Subtask", order_index=1)
    db.add(subtask)
    db.commit()
    db.refresh(subtask)

    response = client.delete(f"/tasks/subtasks/{subtask.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Subtask deleted successfully"}

    deleted_subtask = db.query(Subtask).filter(Subtask.id == subtask.id).first()
    assert deleted_subtask is None


def test_delete_missing_subtask(client):
    response = client.delete("/tasks/subtasks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Subtask not found"}