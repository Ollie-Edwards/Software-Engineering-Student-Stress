from datetime import datetime
import math

# class TaskPreferenceEnum(PyEnum):
#     shortest_first = "shortest_first"
#     easiest_first = "easiest_first"
#     importance_first = "importance_first"
#     due_date_first = "due_date_first"

def urgency_score(due_at, k=0.5):
    now = datetime.now()
    delta_hours = max((due_at - now).total_seconds() / 3600, 0)
    return 1 - math.exp(-k * (24 - delta_hours))

def default_priority_scoring(task):
    # completed tasks have zero priority
    if task.completed:
        return 0

    importance = task.importance / 10
    length = 1 - (task.length - 5) / (300 - 5)  # shorter tasks slightly favored
    urgency = urgency_score(task.due_at)
    tags = 1 if 'critical' in task.tags else 0
    age = min((datetime.utcnow() - task.created_at).days / 30, 1)

    # weights
    w_imp, w_len, w_urg, w_tag, w_age = 4, 1, 5, 3, 1
    score = (w_imp*importance + w_len*length + w_urg*urgency + w_tag*tags + w_age*age) / (w_imp + w_len + w_urg + w_tag + w_age)
    
    return round(score * 100)