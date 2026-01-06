-- ===========================================
-- schema.sql — Creates User, Task, SubTask
-- ===========================================

-- For development only (Will delete all existing data)
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
    task_preference task_preference_enum NOT NULL DEFAULT 'importance_first',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ===========================================
-- Tasks
-- ===========================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT false,
    importance SMALLINT NOT NULL DEFAULT 0 CHECK (importance BETWEEN 0 AND 10),
    length SMALLINT NOT NULL DEFAULT 0 CHECK (length BETWEEN 5 AND 300),
    tags VARCHAR(50)[] DEFAULT '{}',
    due_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_task_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- ===========================================
-- SubTasks
-- ===========================================
CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,

    title VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL,
    order_index INTEGER NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_subtask_task
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
