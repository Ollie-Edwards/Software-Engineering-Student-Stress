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

CREATE TYPE task_reminder_method_enum AS ENUM (
    'email',
    'sms',
    'push_notification'
);

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
-- Tasks
-- ===========================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    importance SMALLINT NOT NULL DEFAULT 0 CHECK (importance BETWEEN 0 AND 10),
    length SMALLINT NOT NULL DEFAULT 0 CHECK (length BETWEEN 5 AND 300),
    tags VARCHAR(50)[] DEFAULT '{}',
    due_at TIMESTAMP,
    reminder_enabled BOOLEAN DEFAULT false,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP DEFAULT NULL,

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
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    order_index INTEGER NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP DEFAULT NULL,

    CONSTRAINT fk_subtask_task
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);

-- ===========================================
-- Moodle Proposed Tasks
-- ===========================================
CREATE TABLE moodletasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,

    course_name VARCHAR(255) NOT NULL,
    activity VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    reference_url VARCHAR(255),
    approved BOOLEAN DEFAULT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP DEFAULT NULL,

    CONSTRAINT fk_task_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_moodletasks_user_id ON tasks(user_id);

-- ===========================================
-- Reminders
-- ===========================================
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    status BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    remind_at TIMESTAMP NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_reminder_task FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION set_remind_at()
RETURNS TRIGGER AS $$
DECLARE
    v_due_at TIMESTAMP;
    v_task_reminder_interval INTERVAL;
    v_importance SMALLINT;
BEGIN
    SELECT t.due_at, u.task_reminder_interval, t.importance
    INTO v_due_at, v_task_reminder_interval, v_importance
    FROM tasks AS t
    JOIN users AS u ON t.user_id = u.id
    WHERE t.id = NEW.task_id;

    IF v_due_at IS NULL THEN
        RAISE EXCEPTION 'Cannot create reminder: linked task must have a due date';
    END IF;

    IF v_task_reminder_interval IS NULL THEN
        RAISE EXCEPTION 'Cannot create reminder: user task reminder preference not found';
    END IF;

    IF v_importance <= 7 THEN
        RAISE EXCEPTION 'Cannot create reminder: linked task must be marked as high priority (importance > 7)';
    END IF;

    IF NEW.remind_at IS NULL THEN
        NEW.remind_at := v_due_at - v_task_reminder_interval;
    END IF;

    IF NEW.remind_at < NOW() THEN
        RAISE EXCEPTION 'Cannot create reminder: reminder date must be in the future';
    END IF;

    IF NEW.remind_at > v_due_at THEN
        RAISE EXCEPTION 'Cannot create reminder: reminder date must be before task due date';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_remind_at
BEFORE INSERT ON reminders
FOR EACH ROW
EXECUTE FUNCTION set_remind_at();

-- ===========================================
-- Notifications (enqueue notifications for reminders)
-- ===========================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    delivered BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Link table between notifications and reminders
CREATE TABLE IF NOT EXISTS notification_reminders (
    notification_id INTEGER NOT NULL,
    reminder_id INTEGER NOT NULL,
    CONSTRAINT fk_nr_notification FOREIGN KEY (notification_id) REFERENCES notifications (id) ON DELETE CASCADE,
    CONSTRAINT fk_nr_reminder FOREIGN KEY (reminder_id) REFERENCES reminders (id) ON DELETE CASCADE,
    PRIMARY KEY (notification_id, reminder_id)
);

CREATE OR REPLACE FUNCTION send_reminder()
RETURNS TRIGGER AS $$
DECLARE
    v_title TEXT;
    v_due_at TIMESTAMP;
    v_user_id INTEGER;
    v_notification_id INTEGER;
    v_existing_scheduled TIMESTAMP;
    v_msg_line TEXT;
    v_day DATE;
BEGIN
    -- Only process enabled reminders
    IF NOT NEW.enabled THEN
        RETURN NEW;
    END IF;

    -- Load linked task info
    SELECT t.title, t.due_at, t.user_id
    INTO v_title, v_due_at, v_user_id
    FROM tasks t
    WHERE t.id = NEW.task_id;

    v_day := (NEW.remind_at::date);
    v_msg_line := format('- %s (due %s)', v_title, to_char(v_due_at, 'YYYY-MM-DD HH24:MI'));

    -- Try to find an existing notification for the same user and day
    SELECT id, scheduled_at
    INTO v_notification_id, v_existing_scheduled
    FROM notifications
    WHERE user_id = v_user_id
        AND (scheduled_at::date) = v_day
    ORDER BY scheduled_at
    LIMIT 1;

    IF FOUND THEN
        -- Append the new line to the existing message and adjust scheduled_at to the earliest time
        UPDATE notifications
        SET message = notifications.message || E'\n' || v_msg_line,
            scheduled_at = LEAST(notifications.scheduled_at, NEW.remind_at)
        WHERE id = v_notification_id;

        -- Link the reminder to the existing notification
        INSERT INTO notification_reminders (notification_id, reminder_id)
        VALUES (v_notification_id, NEW.id);
    ELSE
        -- Create a new notification scheduled at the reminder time
        INSERT INTO notifications (user_id, message, scheduled_at)
        VALUES (v_user_id, v_msg_line, NEW.remind_at)
        RETURNING id INTO v_notification_id;

        INSERT INTO notification_reminders (notification_id, reminder_id)
        VALUES (v_notification_id, NEW.id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enqueue_notification
AFTER INSERT ON reminders
FOR EACH ROW
EXECUTE FUNCTION send_reminder();

-- Keep notifications in sync when reminders are updated (remind_at or enabled)
CREATE OR REPLACE FUNCTION update_notification_on_reminder_change()
RETURNS TRIGGER AS $$
DECLARE
    v_notification_id INTEGER;
    v_lines TEXT[];
    v_title TEXT;
    v_due_at TIMESTAMP;
    v_user_id INTEGER;
    v_day DATE;
    v_msg_line TEXT;
BEGIN
    -- If reminder was disabled, remove its links and rebuild/delete notifications
    IF OLD.enabled = TRUE AND NEW.enabled = FALSE THEN
        FOR v_notification_id IN SELECT notification_id FROM notification_reminders WHERE reminder_id = OLD.id
        LOOP
            DELETE FROM notification_reminders WHERE notification_id = v_notification_id AND reminder_id = OLD.id;

            SELECT array_agg(format('- %s (due %s)', t.title, to_char(r.due_at, 'YYYY-MM-DD HH24:MI')) ORDER BY r.remind_at)
            INTO v_lines
            FROM notification_reminders nr
            JOIN reminders r ON nr.reminder_id = r.id
            JOIN tasks t ON r.task_id = t.id
            WHERE nr.notification_id = v_notification_id;

            IF v_lines IS NULL THEN
                DELETE FROM notifications WHERE id = v_notification_id;
            ELSE
                UPDATE notifications
                SET message = array_to_string(v_lines, E'\n'),
                    scheduled_at = (
                        SELECT MIN(r.remind_at)
                        FROM notification_reminders nr2
                        JOIN reminders r ON nr2.reminder_id = r.id
                        WHERE nr2.notification_id = v_notification_id
                    )
                WHERE id = v_notification_id;
            END IF;
        END LOOP;

        RETURN NEW;
    END IF;

    -- If remind_at changed or reminder was enabled, move/attach the reminder to the correct notification
    IF NEW.enabled = TRUE AND (OLD.remind_at IS DISTINCT FROM NEW.remind_at OR OLD.enabled = FALSE) THEN
        -- If it was previously attached somewhere, remove old links and rebuild their notifications
        IF OLD.enabled = TRUE THEN
            FOR v_notification_id IN SELECT notification_id FROM notification_reminders WHERE reminder_id = OLD.id
            LOOP
                DELETE FROM notification_reminders WHERE notification_id = v_notification_id AND reminder_id = OLD.id;

                SELECT array_agg(format('- %s (due %s)', t.title, to_char(r.due_at, 'YYYY-MM-DD HH24:MI')) ORDER BY r.remind_at)
                INTO v_lines
                FROM notification_reminders nr
                JOIN reminders r ON nr.reminder_id = r.id
                JOIN tasks t ON r.task_id = t.id
                WHERE nr.notification_id = v_notification_id;

                IF v_lines IS NULL THEN
                    DELETE FROM notifications WHERE id = v_notification_id;
                ELSE
                    UPDATE notifications
                    SET message = array_to_string(v_lines, E'\n'),
                        scheduled_at = (
                            SELECT MIN(r.remind_at)
                            FROM notification_reminders nr2
                            JOIN reminders r ON nr2.reminder_id = r.id
                            WHERE nr2.notification_id = v_notification_id
                        )
                    WHERE id = v_notification_id;
                END IF;
            END LOOP;
        END IF;

        -- Attach to the notification for the new day (or create one)
        SELECT t.title, t.due_at, t.user_id INTO v_title, v_due_at, v_user_id FROM tasks t WHERE t.id = NEW.task_id;
        v_day := NEW.remind_at::date;
        v_msg_line := format('- %s (due %s)', v_title, to_char(v_due_at, 'YYYY-MM-DD HH24:MI'));

        SELECT id INTO v_notification_id
        FROM notifications
        WHERE user_id = v_user_id
            AND (scheduled_at::date) = v_day
        ORDER BY scheduled_at
        LIMIT 1;

        IF FOUND THEN
            UPDATE notifications
            SET message = notifications.message || E'\n' || v_msg_line,
                scheduled_at = LEAST(notifications.scheduled_at, NEW.remind_at)
            WHERE id = v_notification_id;

            INSERT INTO notification_reminders (notification_id, reminder_id)
            VALUES (v_notification_id, NEW.id)
            ON CONFLICT DO NOTHING;
        ELSE
            INSERT INTO notifications (user_id, message, scheduled_at)
            VALUES (v_user_id, v_msg_line, NEW.remind_at)
            RETURNING id INTO v_notification_id;

            INSERT INTO notification_reminders (notification_id, reminder_id)
            VALUES (v_notification_id, NEW.id);
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_notification_on_reminder_change
AFTER UPDATE OF remind_at, enabled ON reminders
FOR EACH ROW
EXECUTE FUNCTION update_notification_on_reminder_change();

CREATE OR REPLACE FUNCTION update_notification_on_reminder_change()
RETURNS TRIGGER AS $$
DECLARE
    v_notification_id INT;
    v_lines TEXT[];
    v_title TEXT;
    v_due_at TIMESTAMP;
    v_user_id INT;
    v_day DATE;
    v_msg_line TEXT;
BEGIN
    -- If reminder was disabled: remove its links and rebuild/delete notifications
    IF OLD.enabled = TRUE AND NEW.enabled = FALSE THEN
    FOR v_notification_id IN
        SELECT notification_id FROM notification_reminders WHERE reminder_id = OLD.id
    LOOP
        DELETE FROM notification_reminders
        WHERE notification_id = v_notification_id AND reminder_id = OLD.id;

        SELECT array_agg(format('- %s (due %s)', t.title, to_char(r.due_at,'YYYY-MM-DD HH24:MI')) ORDER BY r.remind_at)
        INTO v_lines
        FROM notification_reminders nr
        JOIN reminders r ON nr.reminder_id = r.id
        JOIN tasks t ON r.task_id = t.id
        WHERE nr.notification_id = v_notification_id;

        IF v_lines IS NULL THEN
        DELETE FROM notifications WHERE id = v_notification_id;
        ELSE
        UPDATE notifications SET message = array_to_string(v_lines, E'\n') WHERE id = v_notification_id;
        END IF;
    END LOOP;

    RETURN NEW;
    END IF;

    -- If reminder became enabled (or remind_at changed and you want re-attach), attach/create notification
    IF NEW.enabled = TRUE THEN
    SELECT t.title, t.due_at, t.user_id INTO v_title, v_due_at, v_user_id
    FROM tasks t WHERE t.id = NEW.task_id;

    v_day := NEW.remind_at::date;
    v_msg_line := format('- %s (due %s)', v_title, to_char(v_due_at,'YYYY-MM-DD HH24:MI'));

    SELECT id INTO v_notification_id
    FROM notifications
    WHERE user_id = v_user_id AND (scheduled_at::date) = v_day
    ORDER BY scheduled_at LIMIT 1;

    IF FOUND THEN
        UPDATE notifications
        SET message = notifications.message || E'\n' || v_msg_line,
            scheduled_at = LEAST(notifications.scheduled_at, NEW.remind_at)
        WHERE id = v_notification_id;

        INSERT INTO notification_reminders(notification_id, reminder_id)
        VALUES (v_notification_id, NEW.id)
        ON CONFLICT DO NOTHING;
    ELSE
        INSERT INTO notifications (user_id, message, scheduled_at)
        VALUES (v_user_id, v_msg_line, NEW.remind_at)
        RETURNING id INTO v_notification_id;

        INSERT INTO notification_reminders(notification_id, reminder_id)
        VALUES (v_notification_id, NEW.id);
    END IF;

    RETURN NEW;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_notification_on_reminder_change
AFTER UPDATE OF enabled, remind_at ON reminders
FOR EACH ROW
EXECUTE FUNCTION update_notification_on_reminder_change();