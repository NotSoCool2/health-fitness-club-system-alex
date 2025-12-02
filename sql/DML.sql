-- *-----------------------------
-- SAMPLE DATA FOR FINAL PROJECT
-- *-----------------------------

-- reset any existing data FK oirder
TRUNCATE trainer_availability RESTART IDENTITY CASCADE;
TRUNCATE trainers RESTART IDENTITY CASCADE;

TRUNCATE metrics RESTART IDENTITY CASCADE;
TRUNCATE goals RESTART IDENTITY CASCADE;
TRUNCATE members RESTART IDENTITY CASCADE;

-- *-----------------------------
-- MEMBERS (MAKE 3-5)
-- *-----------------------------

INSERT INTO members (fname, lname, email, password, birthday, gender, class_count) VALUES
('Gloria', 'Li', 'gloria@gmail.com', 'gloria', '2004-04-23', 'Female', 4), -- member_id = 1
('Alex', 'Bon', 'alex@live.ca', 'alex', '2004-12-25', 'Male', 10),
('Clair', 'Alexander', 'clair@outlook.ca', 'clair', '2002-07-28', 'Female', 2),
('Coffee', 'Cream', 'cream@yahoo.com', 'cream', '1999-07-03', 'Female', 12),
('Dubai', 'Chocolate', 'choco@gmail.com', 'chocolate', '2001-03-28', 'Male', 0);

-- *-----------------------------
-- METRICS
-- *-----------------------------

-- Gloria (member_id = 1)
INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate) VALUES
(1, '2025-11-20 10:00:00', 68.5, 28.0, 78),
(1, '2025-11-23 10:00:00', 67.9, 27.5, 76),
(1, '2025-11-27 09:30:00', 67.2, 27.0, 74);

-- Alex (member_id = 2)
INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate) VALUES
(2, '2025-11-18 18:00:00', 82.0, 24.0, 72),
(2, '2025-11-25 18:00:00', 81.5, 23.8, 70);

-- Clair (member_id = 3)
INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate) VALUES
(3, '2025-11-10 08:30:00', 59.0, 22.0, 80);

-- Coffee (member_id = 4)
INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate) VALUES
(4, '2025-11-15 12:00:00', 74.0, 26.0, 75);

-- Dbai (member_id = 5)
INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate) VALUES
(5, '2025-11-22 07:45:00', 90.0, 30.0, 82);

-- *-----------------------------
-- GOALS (progress bar stuff)
-- *-----------------------------

-- Gloria: weight + body fat goals
INSERT INTO goals (member_id, metric_name, current_metric, goal_metric) VALUES
(1, 'weight', 57, 49),
(1, 'body_fat', 22, 16),

-- Alex: weight goal
(2, 'weight', 81.5, 78.0),

-- Clair: resting heart rate goal
(3, 'heart_rate', 80.0, 70.0);

-- -- Coffee: class count / participation -- Removed because id have to change the DDL and i dont want to do that lol
-- (4, 'Classes Attended', 12.0, 20.0);

-- *-----------------------------
-- TRAINERS
-- *-----------------------------

INSERT INTO trainers (fname, lname, email, password, specialization) VALUES
('George', 'Koh', 'george.koh@healthnfitness.com', 'george', 'Strength & Conditioning'),
('Alex', 'Hylton', 'alex.hylton@healthnfitness.com', 'alex', 'Sports Performance Conditioning'),
('Skylar', 'Park', 'skylar.park@healthnfitness.com', 'skylar', 'Mobility Coach'),
('Miguel', 'Diaz', 'miguel.diaz@healthnfitness.com', 'miguel', 'Cardio'),
('Gloria', 'Li', 'gloria.li@healthnfitness.com', 'gloria', 'Weight Loss Coaching');

-- *-----------------------------
-- TRAINER AVAILABILITY
-- ***** USE A SUBQUERY ON EMAILS, DONT HARDCODE THEIR IDS
-- *-----------------------------

-- George wants to do morning times
INSERT INTO trainer_availability (trainer_id, start_time, end_time) VALUES
(
    (SELECT trainer_id FROM trainers WHERE email = 'george.koh@healthnfitness.com'),
    '2025-12-01 09:00:00', '2025-12-01 11:30:00'
),
(
    (SELECT trainer_id FROM trainers WHERE email = 'george.koh@healthnfitness.com'),
    '2025-12-03 09:00:00', '2025-12-03 11:30:00'
);

-- Alex- evening
INSERT INTO trainer_availability (trainer_id, start_time, end_time) VALUES
(
    (SELECT trainer_id FROM trainers WHERE email = 'alex.hylton@healthnfitness.com'),
    '2025-12-01 18:00:00', '2025-12-01 20:00:00'
),
(
    (SELECT trainer_id FROM trainers WHERE email = 'alex.hylton@healthnfitness.com'),
    '2025-12-04 18:30:00', '2025-12-04 20:00:00'
);

-- Skylar- in da afternoonz
INSERT INTO trainer_availability (trainer_id, start_time, end_time) VALUES
(
    (SELECT trainer_id FROM trainers WHERE email = 'skylar.park@healthnfitness.com'),
    '2025-12-02 11:45:00', '2025-12-02 14:00:00'
);

-- Miguel- weekend
INSERT INTO trainer_availability (trainer_id, start_time, end_time) VALUES
(
    (SELECT trainer_id FROM trainers WHERE email = 'miguel.diaz@healthnfitness.com'),
    '2025-12-06 11:00:00', '2025-12-06 13:00:00'
);

-- gloria- flexible
INSERT INTO trainer_availability (trainer_id, start_time, end_time) VALUES
(
    (SELECT trainer_id FROM trainers WHERE email = 'gloria.li@healthnfitness.com'),
    '2025-12-03 15:00:00', '2025-12-03 17:00:00'
);

INSERT INTO admins (email, password) VALUES ('admin@gmail.com', 'administrator');

-- *-----------------------------
-- ROOMS
-- *-----------------------------

INSERT INTO rooms (room_name, max_capacity) VALUES
('101A', 25),
('101B', 35),
('102A', 5),
('102B', 10);

-- *-----------------------------
-- CLASSES
-- *-----------------------------

INSERT INTO room_bookings (room_id, start_time, end_time, purpose) VALUES
(1, '2025-12-05 13:00:00', '2025-12-05 14:30:00', 'group'),
(2, '2025-12-05 17:00:00', '2025-12-05 19:00:00', 'private');

INSERT INTO classes (booking_id, trainer_id) VALUES
(1, (SELECT trainer_id FROM trainers WHERE email = 'gloria.li@healthnfitness.com')),
(2, (SELECT trainer_id FROM trainers WHERE email = 'alex.hylton@healthnfitness.com'));
