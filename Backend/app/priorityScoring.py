from datetime import datetime
import math


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def scoreTask(task, urgencyHorizon=6.0, typicalDuration=1.0, emergencyBuffer=1.1):
    """
    Args:
        Task
            task.importance: User rating 1-10
            task.completed:  Boolean, if the task is completed
            task.length:     Estimated time to complete in minuites
            task.due_at:     Datetime in which the task is due

        Optional Args:
            urgencyHorizon: Hours at which urgency starts ramping
            typicalDuration: Reference point for "short" tasks
            emergencyBuffer: Multiplier for emergency threshold (default 1.1)
                if hoursUntilDue <= durationHours * emergencyBuffer, then we set priority to 100
    """
    # Style parameters
    weightImportance = 0.65
    weightUrgency = 0.30
    weightShortness = 0.25
    antiStarvation = 0.7

    durationHours = max(task.length / 60, 0.01)
    hoursUntilDue = (task.due_at - datetime.now()).total_seconds() / 3600.0

    if task.completed:
        return 0.0

    # Emergency: must start now or very soon
    if hoursUntilDue <= durationHours * emergencyBuffer:
        return 100.0

    # Importance with diminishing returns at high end
    rawImportance = clamp((task.importance - 1.0) / 9.0, 0.0, 1.0)
    userImportanceScore = math.sqrt(rawImportance)

    # Urgency
    # Slack hours is the number of hours we have remaining if we were to complete the task now
    remainingSlackHours = hoursUntilDue - durationHours
    urgencyScore = urgencyHorizon / (urgencyHorizon + remainingSlackHours)
    urgencyScore = clamp(urgencyScore, 0.0, 1.0)

    # Shortness
    shortnessScore = typicalDuration / (typicalDuration + durationHours)
    shortnessScore = clamp(shortnessScore, 0.0, 1.0)

    # Anti-starvation with stronger fade
    pressure = clamp((userImportanceScore + urgencyScore) / 2.0, 0.0, 1.0)
    effectiveShortnessWeight = weightShortness * (1.0 - antiStarvation * pressure)

    # Normalize weights so they sum to the total
    total = weightImportance + weightUrgency + effectiveShortnessWeight
    wI = weightImportance / total
    wU = weightUrgency / total
    wS = effectiveShortnessWeight / total

    # Base score
    score = 100.0 * (wI * userImportanceScore + wU * urgencyScore + wS * shortnessScore)

    # Boost for high-importance AND high-urgency tasks
    if urgencyScore > 0.75 and userImportanceScore > 0.7:
        score = min(score * 1.15, 99.5)

    # Ensure that score is between 0 and 100, and rounded
    return round(clamp(score, 0.0, 100.0))
