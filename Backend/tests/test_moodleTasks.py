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


def test_approve_task(client, db, moodletask_factory):
    moodle_task = moodletask_factory(
        user_id=2,
        course_name="CM22009 - Machine Learning",
        activity="Lab",
        title="Review Lab Solutions",
        reference_url="https://example.com/test",
    )
    db.add(moodle_task)
    db.commit()

    response = client.post(f"/moodletasks/{moodle_task.id}/approve")
    assert response.status_code == 200
    assert response.json() == {"detail": "Task approved"}


def test_reject_task(client, db, moodletask_factory):
    moodle_task = moodletask_factory(
        user_id=2,
        course_name="CM22009 - Machine Learning",
        activity="Lab",
        title="Review Lab Solutions",
        reference_url="https://example.com/test",
    )
    db.add(moodle_task)
    db.commit()

    response = client.post(f"/moodletasks/{moodle_task.id}/reject")
    assert response.status_code == 200
    assert response.json() == {"detail": "Task rejected"}
