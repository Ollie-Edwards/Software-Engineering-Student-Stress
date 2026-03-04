from app.priorityScoring import clamp, scoreTask
from datetime import datetime, timedelta, timezone

# --- clamp tests ---
# the clamp function f(x, low, high) clamps x within the given low, high range


def test_clamp_within_range():
    assert clamp(5, 0, 10) == 5
    assert clamp(1, 0, 10) == 1
    assert clamp(9, 0, 10) == 9
    assert clamp(50, 0, 100) == 50


def test_clamp_below_lo():
    assert clamp(-1, 0, 10) == 0
    assert clamp(-100, 0, 10) == 0
    assert clamp(0, 5, 10) == 5
    assert clamp(-50, -10, 0) == -10


def test_clamp_above_hi():
    assert clamp(15, 0, 10) == 10
    assert clamp(100, 0, 10) == 10
    assert clamp(11, 0, 10) == 10
    assert clamp(5, 0, 3) == 3


def test_clamp_at_boundaries():
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10
    assert clamp(-10, -10, 10) == -10
    assert clamp(10, -10, 10) == 10


# --- scoreTask tests ---


def test_completed_task_returns_zero(task_factory):
    # if a task is complete, it should have a 0 score
    task = task_factory(completed=True)
    assert scoreTask(task) == 0.0


def test_emergency_task_returns_100(task_factory):
    # due in 1 hour, takes 2 hours → already past emergency threshold
    task = task_factory(length=120, due_at=datetime.now() + timedelta(hours=1))
    assert scoreTask(task) == 100.0


def test_emergency_boundary_exact(task_factory):
    # durationHours=1, emergencyBuffer=1.1 → threshold=1.1h
    # due in exactly 1.05 hours (< 1.1) → emergency
    task = task_factory(length=60, due_at=datetime.now() + timedelta(hours=1.05))
    assert scoreTask(task) == 100.0


def test_score_returns_int_or_rounded(task_factory):
    # task scores should be rounded to 1dp
    task = task_factory(importance=5, length=60, due_at=datetime.now() + timedelta(hours=24))
    score = scoreTask(task)
    assert score == round(score, 1)


def test_score_within_valid_range(task_factory):
    # task scores should be bounded 0-100
    task = task_factory(importance=5, length=60, due_at=datetime.now() + timedelta(hours=24))
    score = scoreTask(task)
    assert 0 <= score <= 100


def test_high_importance_scores_higher_than_low(task_factory):
    # under the same conditions, more important tasks
    # should always have a higher score
    task_high = task_factory(importance=10, due_at=datetime.now() + timedelta(hours=24))
    task_low = task_factory(importance=1, due_at=datetime.now() + timedelta(hours=24))
    assert scoreTask(task_high) > scoreTask(task_low)


def test_urgent_task_scores_higher_than_non_urgent(task_factory):
    task_urgent = task_factory(importance=5, due_at=datetime.now() + timedelta(hours=3))
    task_relaxed = task_factory(importance=5, due_at=datetime.now() + timedelta(hours=100))
    assert scoreTask(task_urgent) > scoreTask(task_relaxed)


def test_short_task_scores_slightly_higher_than_long_same_conditions(task_factory):
    # under the same conditions, shorter tasks should have slightly
    # higher priority scores
    task_short = task_factory(importance=5, length=15, due_at=datetime.now() + timedelta(hours=24))
    task_long = task_factory(importance=5, length=480, due_at=datetime.now() + timedelta(hours=24))
    # Shortness weight is small but should still push score up
    assert scoreTask(task_short) > scoreTask(task_long)


def test_high_importance_high_urgency_boost_capped_at_99_5(task_factory):
    # importance 10 and due very soon but not emergency, should
    # have a high score 70-100 but not out of bounds
    task = task_factory(importance=10, length=30, due_at=datetime.now() + timedelta(hours=2))
    score = scoreTask(task)
    assert score <= 100 and score > 70


def test_minimum_importance_task_far_deadline_low_score(task_factory):
    # tasks set far in the future, with low importance, should have a very low score (less than 20)
    task = task_factory(importance=1, length=30, due_at=datetime.now() + timedelta(hours=500))
    score = scoreTask(task)
    assert score < 20


def test_custom_emergency_buffer(task_factory):
    # length=60min => durationHours=1
    # due in 1.5h: with buffer=1.1 => threshold=1.1h, not emergency => should score less than 100
    # with buffer=2.0 => threshold=2.0h, IS emergency => should score 100
    task_no_emergency = task_factory(length=60, due_at=datetime.now() + timedelta(hours=1.5))
    task_emergency = task_factory(length=60, due_at=datetime.now() + timedelta(hours=1.5))
    assert scoreTask(task_no_emergency, emergencyBuffer=1.1) < 100.0
    assert scoreTask(task_emergency, emergencyBuffer=2.0) == 100.0


def test_very_short_length_does_not_crash(task_factory):
    task = task_factory(length=0, due_at=datetime.now() + timedelta(hours=24))
    score = scoreTask(task)
    assert 0 <= score <= 100


def overdue_task_scores_100(task_factory):
    # tasks which are overdue should have a score of 100
    # the function should be able to deal with negative
    # values of "due_in"
    task = task_factory(length=60, due_at=datetime.now(timezone.utc) - timedelta(hours=10))
    assert scoreTask(task) == 100


def test_importance_above_max(task_factory):
    # if importance exceeds 10 then the score should remain bounded
    task = task_factory(importance=999, due_at=datetime.now() + timedelta(hours=24))
    score = scoreTask(task)
    assert 0 <= score <= 100


def test_importance_below_min(task_factory):
    # if importance is less than 0 then the score should remain bounded
    task = task_factory(importance=-10, due_at=datetime.now() + timedelta(hours=24))
    score = scoreTask(task)
    assert 0 <= score <= 100


def test_very_long_task_does_not_crash(task_factory):
    # if length is very long, the score should remain bounded and should not crash
    task = task_factory(length=10000, due_at=datetime.now() + timedelta(hours=24))
    score = scoreTask(task)
    assert 0 <= score <= 100
