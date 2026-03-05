from sqlalchemy.orm import Session
from app.models.moodleTask import MoodleTask

class MoodleService:
    
    # Get all Moodle tasks from the database
    @staticmethod
    def get_tasks(db: Session, user_id: int):
        return db.query(MoodleTask).filter(MoodleTask.user_id == user_id).all()
    
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