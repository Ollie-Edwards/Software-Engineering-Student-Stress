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
