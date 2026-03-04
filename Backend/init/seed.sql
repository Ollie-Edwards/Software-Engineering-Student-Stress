-- ===========================================
-- seed.sql — Inserts sample data for Users, Tasks, SubTasks, MoodleTasks
-- ===========================================

-- ===========================================
-- Users
-- ===========================================
INSERT INTO users (name, date_of_birth, task_preference)
VALUES
('Alice Johnson', '1990-04-12', 'importance_first'),
('Bob Smith', '1985-10-30', 'shortest_first'),
('Charlie Nguyen', '1998-07-19', 'easiest_first');

-- ===========================================
-- Tasks
-- ===========================================
-- Alice's tasks (user_id = 1)
INSERT INTO tasks (user_id, title, description, completed, importance, length, tags, due_at)
VALUES
(1, 'Plan weekly schedule', 'Create a schedule for next week.', FALSE, 5, 60, ARRAY['planning','weekly'], NOW() + INTERVAL '2 hours'),
(1, 'Buy groceries', 'Milk, eggs, vegetables.', TRUE, 2, 30, ARRAY['shopping','errands'], NOW() + INTERVAL '8 hours'),
(1, 'Exercise', '30 minute morning routine.', FALSE, 4, 30, ARRAY['health','fitness'], NOW() + INTERVAL '8 hours');

-- Bob's tasks (user_id = 2)
INSERT INTO tasks (user_id, title, description, completed, importance, length, tags, due_at)
VALUES
(2, 'Finish project report', 'Complete and submit the annual report.', FALSE, 9, 180, ARRAY['work','report'], NOW() + INTERVAL '5 days'),
(2, 'Clean workspace', 'Organize desk and files.', TRUE, 1, 20, ARRAY['cleaning','organization'], NOW() + INTERVAL '12 hours');

-- Charlie's tasks (user_id = 3)
INSERT INTO tasks (user_id, title, description, completed, importance, length, tags, due_at)
VALUES
(3, 'Study for exam', 'Study chapters 1–5.', FALSE, 7, 120, ARRAY['study','exam'], NOW() + INTERVAL '7 days'),
(3, 'Walk the dog', 'Evening walk around the block.', TRUE, 1, 20, ARRAY['pet','exercise'], NOW() + INTERVAL '6 hours');

-- ===========================================
-- SubTasks
-- ===========================================
-- Alice task_id = 1
INSERT INTO subtasks (task_id, title, completed, order_index)
VALUES
(1, 'Review last week', TRUE, 1),
(1, 'Set goals for next week', FALSE, 2),
(1, 'Assign time blocks', FALSE, 3);

-- Bob: task_id = 4 
INSERT INTO subtasks (task_id, title, completed, order_index)
VALUES
(4, 'Write introduction', TRUE, 1),
(4, 'Compile financial data', FALSE, 2),
(4, 'Review with team', FALSE, 3);

-- Charlie: task_id = 6
INSERT INTO subtasks (task_id, title, completed, order_index)
VALUES
(6, 'Read chapter 1', TRUE, 1),
(6, 'Take notes on chapter 2', FALSE, 2),
(6, 'Practice questions', FALSE, 3);

-- ===========================================
-- Moodle Proposed Tasks
-- ===========================================
INSERT INTO moodletasks (user_id, course_name, activity, title, reference_url)
VALUES
-- CM22009 - Week 21 Deep Neural Networks
(2, 'CM22009 - Machine Learning 2', 'Lecture', 'Review Lecture A: Deep Neural Networks', 'https://moodle.bath.ac.uk/course/section.php?id=254855'),
(2, 'CM22009 - Machine Learning 2', 'Lecture', 'Review Lecture B: Deep Neural Networks (Part II) & Loss Functions (Part I)', 'https://moodle.bath.ac.uk/course/section.php?id=254855'),
(2, 'CM22009 - Machine Learning 2', 'Lab', 'Complete Lab Notebook: Deep Neural Networks', 'https://moodle.bath.ac.uk/course/section.php?id=254855'),
(2, 'CM22009 - Machine Learning 2', 'Lab', 'Review Lab Solutions: Deep Neural Networks', 'https://moodle.bath.ac.uk/course/section.php?id=254855'),

-- CM22009 - Week 22 Backpropagation
(2, 'CM22009 - Machine Learning 2', 'Lecture', 'Review Lecture A: Backpropagation', 'https://moodle.bath.ac.uk/course/section.php?id=254856'),
(2, 'CM22009 - Machine Learning 2', 'Lecture', 'Review Lecture B: Loss Functions (Part II) & Coursework Introduction', 'https://moodle.bath.ac.uk/course/section.php?id=254856'),
(2, 'CM22009 - Machine Learning 2', 'Lab', 'Complete Lab Notebooks: Gradient I and Gradient II', 'https://moodle.bath.ac.uk/course/section.php?id=254856'),
(2, 'CM22009 - Machine Learning 2', 'Lab', 'Review Lab Solutions: Gradient I and Gradient II', 'https://moodle.bath.ac.uk/course/section.php?id=254856'),

-- CM22009 - Week 23 Loss Functions & Regularization
(2, 'CM22009 - Machine Learning 2', 'Lecture', 'Review Lecture A: Loss Functions & Measuring Performance', 'https://moodle.bath.ac.uk/course/section.php?id=254857'),
(2, 'CM22009 - Machine Learning 2', 'Lecture', 'Review Lecture B: Regularization', 'https://moodle.bath.ac.uk/course/section.php?id=254857'),

-- CM22007 - Week 21 Code Coverage and Containers
(2, 'CM22007 - Software Engineering 2', 'Lecture', 'Review Lecture 1: Code Coverage', 'https://moodle.bath.ac.uk/course/section.php?id=255588'),
(2, 'CM22007 - Software Engineering 2', 'Lecture', 'Review Lecture 2: Docker', 'https://moodle.bath.ac.uk/course/section.php?id=255588'),
(2, 'CM22007 - Software Engineering 2', 'Tutorial', 'Review Week 21 Tutorial Slides', 'https://moodle.bath.ac.uk/course/section.php?id=255588'),

-- CM22007 - Week 22 DevOps
(2, 'CM22007 - Software Engineering 2', 'Lecture', 'Review Lecture 1: DevOps I', 'https://moodle.bath.ac.uk/course/section.php?id=256225'),
(2, 'CM22007 - Software Engineering 2', 'Lecture', 'Review Lecture 2: DevOps II', 'https://moodle.bath.ac.uk/course/section.php?id=256225'),
(2, 'CM22007 - Software Engineering 2', 'Tutorial', 'Review Week 22 Tutorial Slides', 'https://moodle.bath.ac.uk/course/section.php?id=256225'),

-- CM22007 - Week 23 The AI Software Engineer
(2, 'CM22007 - Software Engineering 2', 'Lecture', 'Review Lecture 1: The AI Software Engineer I', 'https://moodle.bath.ac.uk/course/section.php?id=256901'),
(2, 'CM22007 - Software Engineering 2', 'Lecture', 'Review Lecture 2: The AI Software Engineer II', 'https://moodle.bath.ac.uk/course/section.php?id=256901'),
(2, 'CM22007 - Software Engineering 2', 'Independent Study', 'Read Independent Study Guidelines: VSCode', 'https://moodle.bath.ac.uk/course/section.php?id=256901'),
(2, 'CM22007 - Software Engineering 2', 'Independent Study', 'Read Independent Study Guidelines: CoPilot', 'https://moodle.bath.ac.uk/course/section.php?id=256901');
