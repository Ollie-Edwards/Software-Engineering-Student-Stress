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
(2, 'CM22008 - Algorithms and Complexity', 'Exercise', 'Complete Exercise 1', 'https://moodle.bath.ac.uk/mod/resource/view.php?id=1361324'),
(2, 'CM22008 - Algorithms and Complexity', 'Lecture', 'Review Lecture 1: Introduction', 'https://uniofbath.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=80dfa01a-65fd-4369-b5c6-b36700fbade1'),
(2, 'CM22008 - Algorithms and Complexity', 'Lecture', 'Review Lecture 2: Finite automata and regular languages', 'https://uniofbath.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=6ee4238d-d104-4f5c-8570-b36a0056ed81');
