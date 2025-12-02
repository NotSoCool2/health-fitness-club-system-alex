-- Member Section

DROP TABLE IF EXISTS members CASCADE;

DROP TABLE IF EXISTS metrics CASCADE;

DROP TABLE IF EXISTS goals CASCADE;

CREATE TABLE IF NOT EXISTS members (
	member_id	SERIAL PRIMARY KEY,
	fname		TEXT NOT NULL,
	lname		TEXT NOT NULL,
	email		TEXT UNIQUE,
	password	TEXT NOT NULL,
	birthday	DATE NOT NULL,
	gender		TEXT NOT NULL,
	class_count	INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS metrics (
	metric_id	SERIAL PRIMARY KEY,
	member_id	INT REFERENCES members(member_id),
	metric_date	TIMESTAMP NOT NULL,
	weight		FLOAT,
	body_fat	FLOAT,
	heart_rate	FLOAT
);

CREATE TABLE IF NOT EXISTS goals (
	goal_id			SERIAL PRIMARY KEY,
	member_id		INT REFERENCES members(member_id),
	metric_name		TEXT NOT NULL,
	current_metric	FLOAT NOT NULL,
	goal_metric		FLOAT NOT NULL,

	UNIQUE(member_id, metric_name)
);

-- Update the goal data when new metrics are inserted

CREATE OR REPLACE FUNCTION update_goals()
RETURNS trigger AS $$
BEGIN
	UPDATE goals
	SET current_metric = NEW.weight
	WHERE goals.member_id = NEW.member_id
	AND goals.metric_name = 'weight';

	UPDATE goals
	SET current_metric = NEW.body_fat
	WHERE goals.member_id = NEW.member_id
	AND goals.metric_name = 'body_fat';

	UPDATE goals
	SET current_metric = NEW.heart_rate
	WHERE goals.member_id = NEW.member_id
	AND goals.metric_name = 'heart_rate';

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER metrics_update_goals
AFTER INSERT ON metrics
FOR EACH ROW
EXECUTE FUNCTION update_goals();

-- *** GLORIA Trainer Section
-- Trainer + Availability

DROP TABLE IF EXISTS trainer_availability CASCADE;

DROP TABLE IF EXISTS trainers CASCADE;

CREATE TABLE trainers (
    trainer_id      SERIAL PRIMARY KEY,
    fname           TEXT NOT NULL,
    lname           TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
	password		TEXT NOT NULL,
    specialization  TEXT
);

CREATE TABLE trainer_availability (
    slot_id     SERIAL PRIMARY KEY,
    trainer_id  INT NOT NULL REFERENCES trainers(trainer_id),
    start_time  TIMESTAMP NOT NULL,
    end_time    TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS admins CASCADE;

DROP TABLE IF EXISTS rooms CASCADE;

DROP TABLE IF EXISTS room_bookings CASCADE;

DROP TABLE IF EXISTS classes CASCADE;

DROP VIEW IF EXISTS available_classes CASCADE;

DROP TABLE IF EXISTS class_regs CASCADE;

CREATE TABLE admins (
	admin_id	SERIAL PRIMARY KEY,
	email		TEXT UNIQUE NOT NULL,
	password	TEXT NOT NULL
);

CREATE TABLE rooms (
	room_id			SERIAL PRIMARY KEY,
	room_name		TEXT UNIQUE NOT NULL,
	max_capacity	INT CHECK (max_capacity > 0)
);

CREATE TABLE room_bookings (
	booking_id	SERIAL PRIMARY KEY,
	room_id		INT NOT NULL REFERENCES rooms(room_id),
	start_time	TIMESTAMP NOT NULL,
	end_time	TIMESTAMP NOT NULL CHECK (end_time > start_time),
	purpose		TEXT NOT NULL
);

CREATE TABLE classes (
	class_id	SERIAL PRIMARY KEY,
	booking_id	INT UNIQUE NOT NULL REFERENCES room_bookings(booking_id),
	trainer_id	INT NOT NULL REFERENCES trainers(trainer_id),
	attendance	INT NOT NULL DEFAULT 0
);

CREATE VIEW available_classes AS
SELECT 
    c.class_id, (t.fname||' '||t.lname) as trainer_name, rb.purpose, rb.start_time, rb.end_time, r.room_name, c.attendance,
    CASE
        WHEN rb.purpose = 'private' THEN 1
        ELSE r.max_capacity
    END AS capacity

FROM classes c
JOIN trainers t ON c.trainer_id = t.trainer_id
JOIN room_bookings rb ON c.booking_id = rb.booking_id
JOIN rooms r ON rb.room_id = r.room_id
WHERE c.attendance < CASE
	WHEN rb.purpose = 'private' THEN 1
	ELSE r.max_capacity
END;

CREATE TABLE class_regs (
	reg_id		SERIAL PRIMARY KEY,
	class_id	INT NOT NULL REFERENCES classes(class_id),
	member_id	INT NOT NULL REFERENCES members(member_id)
);