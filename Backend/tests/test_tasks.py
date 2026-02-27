from datetime import datetime, timezone
from app.models.task import Task

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
