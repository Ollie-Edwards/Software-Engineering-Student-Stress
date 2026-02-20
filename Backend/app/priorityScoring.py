from datetime import datetime
import math


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def scoreTask(task, urgencyHorizon=4.0, typicalDuration=2.0, emergencyBuffer=1.1):
    """
    Score a task from 0-100 based on importance, urgency, and duration.

    Args:
        task.importance: User rating 1-10
        durationHours: Estimated time to complete in hours
        hoursUntilDue: Hours remaining until deadline
        urgencyHorizon: Hours at which urgency starts ramping (default 4)
        typicalDuration: Reference point for "short" tasks (default 2)
        emergencyBuffer: Multiplier for emergency threshold (default 1.1)
    """
    # Style parameters
    weightImportance = 0.65  # Increased from 0.60
    weightUrgency = 0.30
    weightShortness = 0.05  # Decreased from 0.10
    antiStarvation = 0.7  # Increased from 0.6

    # completed: bool  # Whether or not the task is complete
    # importance: int  # How important the task is (scale from 1-10)
    # length: int  # How many minuites this will take (<5 - 300)
    # due_at: Optional[datetime] = None  # The date that this must be completed by

    durationHours = max(task.length / 60, 0.01)
    hoursUntilDue = (task.due_at - datetime.now()).total_seconds() / 3600.0

    if task.completed:
        return 0.0

    # Emergency: must start now or very soon
    if hoursUntilDue <= durationHours * emergencyBuffer:
        return 100.0

    # Importance with diminishing returns at high end
    rawImportance = clamp((task.importance - 1.0) / 9.0, 0.0, 1.0)
    userImportanceScore = math.sqrt(rawImportance)  # Slight compression

    # Urgency
    remainingSlackHours = hoursUntilDue - durationHours
    urgencyScore = urgencyHorizon / (urgencyHorizon + remainingSlackHours)
    urgencyScore = clamp(urgencyScore, 0.0, 1.0)

    # Shortness
    shortnessScore = typicalDuration / (typicalDuration + durationHours)
    shortnessScore = clamp(shortnessScore, 0.0, 1.0)

    # Anti-starvation with stronger fade
    pressure = clamp((userImportanceScore + urgencyScore) / 2.0, 0.0, 1.0)
    effectiveShortnessWeight = weightShortness * (1.0 - antiStarvation * pressure)

    # Normalize weights
    total = weightImportance + weightUrgency + effectiveShortnessWeight
    wI = weightImportance / total
    wU = weightUrgency / total
    wS = effectiveShortnessWeight / total

    # Base score
    score = 100.0 * (wI * userImportanceScore + wU * urgencyScore + wS * shortnessScore)

    # Boost for high-importance AND high-urgency tasks
    if urgencyScore > 0.75 and userImportanceScore > 0.7:
        score = min(score * 1.15, 99.5)  # Cap below emergency level

    return round(clamp(score, 0.0, 100.0))
