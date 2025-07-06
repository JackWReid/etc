CREATE TABLE IF NOT EXISTS guests (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    home TEXT,
    side TEXT,
    diet TEXT,
    "group" TEXT,
    confirmed TEXT,
    lastEdited TEXT NOT NULL
);

INSERT INTO guests (id, name, email, home, side, diet, "group", confirmed, lastEdited) VALUES
    ('1', 'John Doe', 'john@doe.com', 'Bristol', 'Sarah', 'Omni', '1', '1', '2019-01-01 00:00:00');

CREATE TABLE IF NOT EXISTS gifts (
    id TEXT PRIMARY KEY,
    lastEdited TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    rrp REAL,
    category TEXT,
    purchased TEXT
);

INSERT INTO gifts (id, name, url, rrp, category, purchased, lastEdited) VALUES
    ('1', 'Le Creuset cafetiere (Blue)', 'https://www.kadewe.de', 70, 'Home', null, '2023-12-08 09:15:00');
    
CREATE TABLE IF NOT EXISTS gift_submission (
    gift TEXT NOT NULL,
    guest TEXT NOT NULL,
    lastEdited TEXT NOT NULL
);

INSERT INTO gift_submission (gift, guest, lastEdited) VALUES
    ('Le Creuset cafetiere (Blue)', 'John Doe', '2023-12-08 09:15:00');

CREATE TABLE IF NOT EXISTS rsvp_submission (
    name TEXT NOT NULL,
    response TEXT NOT NULL,
    dietary TEXT,
    comments TEXT,
    lastEdited TEXT NOT NULL
);

INSERT INTO rsvp_submission (name, response, dietary, comments, lastEdited) VALUES
    ('John Doe', 'Yes', 'Vegetarian', 'Looking forward to it!', '2023-12-08 09:15:00');
