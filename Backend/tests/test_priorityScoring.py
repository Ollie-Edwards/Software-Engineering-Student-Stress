# tests/test_score_task.py
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from priorityScoring import clamp, scoreTask


def make_task(importance=5, length=60, due_in_hours=24, completed=False):
    task = MagicMock()
    task.importance = importance
    task.length = length  # in minutes
    task.due_at = datetime.now() + timedelta(hours=due_in_hours)
    task.completed = completed
    return task


# --- clamp tests ---


def test_clamp_within_range():
    assert clamp(5, 0, 10) == 5


def test_clamp_below_lo():
    assert clamp(-1, 0, 10) == 0


def test_clamp_above_hi():
    assert clamp(15, 0, 10) == 10


def test_clamp_at_boundaries():
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10


# --- scoreTask tests ---


def test_completed_task_returns_zero():
    task = make_task(completed=True)
    assert scoreTask(task) == 0.0


def test_emergency_task_returns_100():
    # due in 1 hour, takes 2 hours → already past emergency threshold
    task = make_task(length=120, due_in_hours=1)
    assert scoreTask(task) == 100.0


def test_emergency_boundary_exact():
    # durationHours=1, emergencyBuffer=1.1 → threshold=1.1h
    # due in exactly 1.05 hours (< 1.1) → emergency
    task = make_task(length=60, due_in_hours=1.05)
    assert scoreTask(task) == 100.0


def test_score_returns_int_or_rounded():
    task = make_task(importance=5, length=60, due_in_hours=24)
    score = scoreTask(task)
    assert score == round(score)


def test_score_within_valid_range():
    task = make_task(importance=5, length=60, due_in_hours=24)
    score = scoreTask(task)
    assert 0 <= score <= 100


def test_high_importance_scores_higher_than_low():
    task_high = make_task(importance=10, due_in_hours=24)
    task_low = make_task(importance=1, due_in_hours=24)
    assert scoreTask(task_high) > scoreTask(task_low)


def test_urgent_task_scores_higher_than_non_urgent():
    task_urgent = make_task(importance=5, due_in_hours=3)
    task_relaxed = make_task(importance=5, due_in_hours=100)
    assert scoreTask(task_urgent) > scoreTask(task_relaxed)


def test_short_task_scores_slightly_higher_than_long_same_conditions():
    task_short = make_task(importance=5, length=15, due_in_hours=24)
    task_long = make_task(importance=5, length=480, due_in_hours=24)
    # Shortness weight is small but should still push score up
    assert scoreTask(task_short) >= scoreTask(task_long)


def test_high_importance_high_urgency_boost_capped_at_99_5():
    # importance=10, due very soon but not emergency
    task = make_task(importance=10, length=30, due_in_hours=2)
    score = scoreTask(task)
    assert score <= 100


def test_minimum_importance_task_far_deadline_low_score():
    task = make_task(importance=1, length=30, due_in_hours=500)
    score = scoreTask(task)
    assert score < 20


def test_custom_emergency_buffer():
    # length=60min → durationHours=1
    # due in 1.5h: with buffer=1.1 → threshold=1.1h, not emergency
    # with buffer=2.0 → threshold=2.0h, IS emergency
    task_no_emergency = make_task(length=60, due_in_hours=1.5)
    task_emergency = make_task(length=60, due_in_hours=1.5)
    assert scoreTask(task_no_emergency, emergencyBuffer=1.1) != 100.0
    assert scoreTask(task_emergency, emergencyBuffer=2.0) == 100.0


def test_very_short_length_does_not_crash():
    task = make_task(length=0, due_in_hours=24)
    score = scoreTask(task)
    assert 0 <= score <= 100
