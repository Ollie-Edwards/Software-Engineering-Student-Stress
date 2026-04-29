-- ===========================================
-- RESET
-- ===========================================
DROP TABLE IF EXISTS subtasks CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS moodletasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS task_preference_enum CASCADE;
DROP TYPE IF EXISTS task_reminder_method_enum CASCADE;

-- ===========================================
-- ENUMS
-- ===========================================
CREATE TYPE task_preference_enum AS ENUM (
    'shortest_first',
    'easiest_first',
    'importance_first',
    'due_date_first'
);

CREATE TYPE task_reminder_method_enum AS ENUM (
    'email',
    'sms',
    'push_notification'
);

-- ===========================================
-- USERS
-- ===========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    task_preference task_preference_enum NOT NULL DEFAULT 'importance_first',

    task_reminder_interval INTERVAL NOT NULL DEFAULT '1 day',
    task_reminder_method task_reminder_method_enum NOT NULL DEFAULT 'email',

    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ===========================================
-- TASKS
-- ===========================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    completed BOOLEAN NOT NULL DEFAULT FALSE,

    importance SMALLINT NOT NULL DEFAULT 0
        CHECK (importance BETWEEN 0 AND 10),

    length SMALLINT NOT NULL DEFAULT 0
        CHECK (length BETWEEN 5 AND 300),

    tags TEXT[],

    due_at TIMESTAMP,
    reminder_enabled BOOLEAN DEFAULT FALSE,

    reference_url VARCHAR(255),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    CONSTRAINT fk_task_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- ===========================================
-- SUBTASKS
-- ===========================================
CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,

    title VARCHAR(255) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    order_index INTEGER NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    CONSTRAINT fk_subtask_task
        FOREIGN KEY (task_id)
        REFERENCES tasks (id)
        ON DELETE CASCADE
);

CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);

-- ===========================================
-- MOODLE TASKS
-- ===========================================
CREATE TABLE moodletasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,

    course_name VARCHAR(255) NOT NULL,
    activity VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    reference_url VARCHAR(255) NOT NULL,

    approved BOOLEAN DEFAULT NULL,

    due_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP,

    CONSTRAINT fk_moodletask_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

CREATE INDEX idx_moodletasks_user_id ON moodletasks(user_id);