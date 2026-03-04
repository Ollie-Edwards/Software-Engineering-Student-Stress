def test_complete_task_success(client, db, task_factory):
    task = task_factory()

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/tasks/task/{task.id}/complete")

    assert response.status_code == 200
    assert response.json() == {"message": "Task completed"}

    db.refresh(task)
    assert task.completed is True
    assert task.completed_at is not None
