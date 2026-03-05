from app.models.moodleTask import MoodleTask
from app.models.task import Task
from app.moodleService import MoodleService

# get_tasks
def test_get_tasks_returns_correct_tasks(db, moodletask_factory):
    task1 = moodletask_factory(user_id=2)
    task2 = moodletask_factory(user_id=2)
    task_other = moodletask_factory(user_id=99)

    db.add_all([task1, task2, task_other])
    db.commit()

    tasks = MoodleService.get_tasks(db, user_id=2)

    assert len(tasks) == 2

# get_task_by_id
def test_get_task_by_id_returns_task(db, moodletask_factory):
    task = moodletask_factory(user_id=2)

    db.add(task)
    db.commit()

    retrieved = MoodleService.get_task_by_id(db, task.id)

    assert retrieved.id == task.id

def test_get_task_by_id_returns_none(db):
    task = MoodleService.get_task_by_id(db, 999)

    assert task is None

# get_pending_tasks
def test_get_pending_tasks_unapproved(db, moodletask_factory):
    task_pending = moodletask_factory(user_id=2, approved=None)
    task_approved = moodletask_factory(user_id=2, approved=True)

    db.add_all([task_pending, task_approved])
    db.commit()

    tasks = MoodleService.get_pending_tasks(db, user_id=2)

    assert len(tasks) == 1
    assert tasks[0].approved is None

# approve_task
def test_approve_task_creates_new_task(db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=None)

    db.add(task)
    db.commit()

    approved_task = MoodleService.approve_task(db, task.id)

    db.refresh(task)

    assert approved_task.approved is True

    # Check that a new Task was added
    new_task = db.query(Task).filter(Task.title == task.title).first()

    assert new_task is not None
    assert new_task.user_id == task.user_id

def test_approve_task_already_modified(db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=True)

    db.add(task)
    db.commit()

    result = MoodleService.approve_task(db, task.id)

    assert result == "already modified"

def test_approve_task_not_found(db):
    result = MoodleService.approve_task(db, 999)

    assert result is None

# reject_task
def test_reject_task(db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=None)

    db.add(task)
    db.commit()

    rejected_task = MoodleService.reject_task(db, task.id)
    db.refresh(task)

    assert rejected_task.approved is False

def test_reject_task_already_modified(db, moodletask_factory):
    task = moodletask_factory(user_id=2, approved=True)

    db.add(task)
    db.commit()

    result = MoodleService.reject_task(db, task.id)

    assert result == "already modified"

def test_reject_task_not_found(db):
    result = MoodleService.reject_task(db, 999)

    assert result is None

# sync_tasks
def test_sync_tasks_creates_tasks(db):
    tasks_created = MoodleService.sync_tasks(db, user_id=2)

    assert len(tasks_created) > 0

    # Check that they are in the database
    db_tasks = db.query(MoodleTask).filter(MoodleTask.user_id == 2).all()

    assert len(db_tasks) == len(tasks_created)

def test_sync_tasks_does_not_create_duplicates(db):
    MoodleService.sync_tasks(db, user_id=2)
    tasks_created = MoodleService.sync_tasks(db, user_id=2)

    # Should not create new ones
    assert tasks_created == []