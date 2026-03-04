def test_enable_reminders_success(client, db, task_factory):
    task = task_factory(reminder_enabled=False)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/enable_reminders")

    assert response.status_code == 200
    assert response.json() == {"message": "Task reminder enabled"}

    db.refresh(task)
    assert task.reminder_enabled is True


def test_enable_reminders_already_enabled(client, db, task_factory):
    task = task_factory(reminder_enabled=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/enable_reminders")

    assert response.status_code == 400
    assert response.json() == {"detail": "Reminders already enabled"}


def test_enable_reminders_missing_task(client):
    response = client.post("/reminders/234/enable_reminders")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_disable_reminders_success(client, db, task_factory):
    task = task_factory(reminder_enabled=True)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/disable_reminders")

    assert response.status_code == 200
    assert response.json() == {"message": "Task reminder disabled"}

    db.refresh(task)
    assert task.reminder_enabled is False


def test_disable_reminders_already_disabled(client, db, task_factory):
    task = task_factory(reminder_enabled=False)

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/reminders/{task.id}/disable_reminders")

    assert response.status_code == 400
    assert response.json() == {"detail": "Task reminders already disabled"}


def test_disable_reminders_missing_task(client):
    response = client.post("/reminders/234/disable_reminders")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
