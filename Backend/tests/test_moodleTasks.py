from app.models.moodleTask import MoodleTask
from app.models.task import Task

def test_moodle_tasks_success(client, db, moodletask_factory):
    task1 = moodletask_factory(user_id=2)
    task2 = moodletask_factory(user_id=2)

    db.add_all([task1, task2])
    db.commit()

    response = client.get("/moodletasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_moodle_tasks_not_found(client):
    response = client.get("/moodletasks")

    assert response.status_code == 404
    assert response.json() == {"detail": "No Tasks Found"}


def test_get_moodle_tasks_only_returns_correct_user(client, db, moodletask_factory):
    task_user_2 = moodletask_factory(user_id=2)
    task_other = moodletask_factory(user_id=99)

    db.add_all([task_user_2, task_other])
    db.commit()

    response = client.get("/moodletasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

# GET /moodletasks/pending

def test_get_pending_tasks(client, db, moodletask_factory):
    pending_task = moodletask_factory(user_id=2, approved=None)
    approved_task = moodletask_factory(user_id=2, approved=True)

    db.add_all([pending_task, approved_task])
    db.commit()

    response = client.get("/moodletasks/pending")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_get_pending_tasks_not_found(client, db, moodletask_factory):
    approved_task = moodletask_factory(user_id=2, approved=True)
    rejected_task = moodletask_factory(user_id=2, approved=False)

    db.add_all([approved_task, rejected_task])
    db.commit()

    response = client.get("/moodletasks/pending")

    assert response.status_code == 404
    assert response.json() == {"detail": "No Tasks Found"}

# POST /moodletasks/sync

def test_sync_moodle_tasks_creates_tasks(client, db):
    response = client.post("/moodletasks/sync")

    assert response.status_code == 200
    data = response.json()
    assert "tasks_created" in data
    assert data["tasks_created"] > 0

    # Check tasks exist in database
    tasks_in_db = db.query(MoodleTask).filter(MoodleTask.user_id == 2).all()
    assert len(tasks_in_db) == data["tasks_created"]

def test_sync_moodle_tasks_no_duplicates(client):
    client.post("/moodletasks/sync")
    response = client.post("/moodletasks/sync")
    
    data = response.json()
    assert data["tasks_created"] == 0

# POST /moodletasks/{task_id}/approve

def test_approve_task(client, db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=None)
    db.add(task)
    db.commit()

    response = client.post(f"/moodletasks/{task.id}/approve")

    assert response.status_code == 200
    assert response.json() == {"message": "Task approved"}

    # Check MoodleTask is approved
    db.refresh(task)

    assert task.approved is True

    # Check Task was created
    new_task = db.query(Task).filter(Task.title == task.title).first()

    assert new_task is not None

def test_approve_task_already_modified(client, db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=True)
    db.add(task)
    db.commit()

    response = client.post(f"/moodletasks/{task.id}/approve")
    assert response.status_code == 400
    assert response.json()["detail"] == "Task has already been approved/rejected"

def test_approve_task_not_found(client):
    response = client.post("/moodletasks/999/approve")
    assert response.status_code == 404
    assert response.json()["detail"] == "No Task Found"

# POST /moodletasks/{task_id}/reject

def test_reject_task(client, db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=None)

    db.add(task)
    db.commit()

    response = client.post(f"/moodletasks/{task.id}/reject")

    assert response.status_code == 200
    assert response.json() == {"message": "Task rejected"}

    db.refresh(task)

    assert task.approved is False

def test_reject_task_already_modified(client, db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=True)

    db.add(task)
    db.commit()

    response = client.post(f"/moodletasks/{task.id}/reject")

    assert response.status_code == 400
    assert response.json()["detail"] == "Task has already been approved/rejected"

def test_reject_task_not_found(client):
    response = client.post("/moodletasks/999/reject")

    assert response.status_code == 404
    assert response.json()["detail"] == "No Task Found"