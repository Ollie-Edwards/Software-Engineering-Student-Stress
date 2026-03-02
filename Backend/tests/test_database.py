from datetime import datetime, timezone
from app.models.task import Task


def test_complete_task_success(client, db):
    task = Task(
        user_id=1,
        title="Test Task",
        description="Test description",
        completed=False,
        importance=5,
        length=30,
        tags=[],
        due_at=datetime.now(timezone.utc),
        reminder_enabled=False,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.post(f"/tasks/task/{task.id}/complete")

    assert response.status_code == 200
    assert response.json() == {"message": "Task completed"}

    db.refresh(task)
    assert task.completed is True
    assert task.completed_at is not None
