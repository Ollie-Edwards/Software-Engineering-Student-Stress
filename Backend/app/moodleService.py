from sqlalchemy.orm import Session
from app.models.moodleTask import MoodleTask
from app.models.task import Task
from datetime import datetime, timezone

class MoodleService:
    
    # Get all Moodle tasks from the database
    @staticmethod
    def get_tasks(db: Session, user_id: int):
        return db.query(MoodleTask).filter(MoodleTask.user_id == user_id).all()
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int):
        return db.query(MoodleTask).filter(MoodleTask.id == task_id).first()
    
    @staticmethod
    def get_pending_tasks(db: Session, user_id: int):
        return db.query(MoodleTask).filter(
            MoodleTask.user_id == user_id,
            MoodleTask.approved == None
        ).all()
    
    @staticmethod
    def approve_task(db: Session, task_id: int):
        moodle_task = MoodleService.get_task_by_id(db, task_id)

        if not moodle_task:
            return None
        
        if moodle_task.approved is not None:
            return "already modified"
        
        moodle_task.approved = True
        moodle_task.approved_at = datetime.now(timezone.utc)

        # Add to user's tasks
        new_task = Task(
            user_id = moodle_task.user_id,
            title = moodle_task.title
        )

        db.add(new_task)
        db.commit()

        return moodle_task
    
    @staticmethod
    def reject_task(db: Session, task_id: int):
        moodle_task = MoodleService.get_task_by_id(db, task_id)

        if not moodle_task:
            return None
        
        if moodle_task.approved is not None:
            return "already modified"
        
        moodle_task.approved = False

        db.commit()

        return moodle_task
    
    # Simulate Moodle API response
    @staticmethod
    def fetch_tasks():
        return [
            {
                "course_name": "Machine Learning",
                "activity": "Lecture",
                "title": "Introduction to Supervised Learning",
                "reference_url": "https://moodle.tasks/101",
            },
            {
                "course_name": "Machine Learning",
                "activity": "Lecture",
                "title": "Logistic Regression",
                "reference_url": "https://moodle.tasks/102",
            },
            {
                "course_name": "Machine Learning",
                "activity": "Lab",
                "title": "Linear Regression",
                "reference_url": "https://moodle.tasks/103",
            },
            {
                "course_name": "Machine Learning",
                "activity": "Coursework",
                "title": "Regression Experiments",
                "reference_url": "https://moodle.tasks/104",
            },
        ]
    
    # Sync Moodle tasks to database
    @staticmethod
    def sync_tasks(db: Session, user_id: int):
        tasks = MoodleService.fetch_tasks()
        tasks_created = []

        for task in tasks:
            task_exists = (db.query(MoodleTask).filter(
                MoodleTask.user_id == user_id,
                MoodleTask.course_name == task["course_name"],
                MoodleTask.activity == task["activity"],
                MoodleTask.title == task["title"],).first())
            
            if not task_exists:
                new_task = MoodleTask(
                    user_id = user_id,
                    course_name = task["course_name"],
                    activity = task["activity"],
                    title = task["title"],
                    reference_url = task["reference_url"],
                )
                db.add(new_task)
                tasks_created.append(new_task)

        db.commit()
        return tasks_created