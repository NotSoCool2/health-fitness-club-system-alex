-- Member Section

DROP TABLE IF EXISTS members CASCADE;

DROP TABLE IF EXISTS metrics CASCADE;

DROP TABLE IF EXISTS goals CASCADE;

CREATE TABLE IF NOT EXISTS members (
	member_id	SERIAL PRIMARY KEY,
	fname		TEXT NOT NULL,
	lname		TEXT NOT NULL,
	email		TEXT UNIQUE NOT NULL,
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