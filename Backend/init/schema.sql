-- ===========================================
-- schema.sql — Creates User, Task, SubTask
-- ===========================================

-- Drop tables (dev only)
DROP TABLE IF EXISTS subtasks CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ===========================================
-- Users
-- ===========================================
CREATE TYPE task_preference_enum AS ENUM (
    'shortest_first',
    'easiest_first',
    'importance_first',
    'due_date_first'
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    task_preference task_preference_enum DEFAULT 'importance_first',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===========================================
-- Tasks
-- ===========================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status BOOLEAN NOT NULL,
    importance SMALLINT NOT NULL DEFAULT 0 CHECK (importance BETWEEN 0 AND 100),
    length INTEGER,
    tag_id INTEGER,
    due_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_task_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- all tasks belonging to one user
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- ===========================================
-- SubTasks
-- ===========================================
CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,

    title VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL,
    order_index INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_subtask_task
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
);

-- Index to speed up “get subtasks for task”
CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
