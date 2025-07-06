CREATE TABLE IF NOT EXISTS book (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  author TEXT,
  image_url TEXT,
  description TEXT,
  status_read TEXT DEFAULT 'not-read',
  status_owned TEXT DEFAULT 'not-owned',
  isbn TEXT UNIQUE,
  isbn13 TEXT UNIQUE,
  asin TEXT UNIQUE,
  oku_id TEXT UNIQUE,
  goodreads_id TEXT UNIQUE,
  amazon_id TEXT UNIQUE,
  date_published TIMESTAMP,
  date_last_read_event TIMESTAMP,
  date_last_owned_event TIMESTAMP,
  date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT,
  book_id INTEGER,
  date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (book_id) REFERENCES book(id),
  UNIQUE(event_type, book_id, date_created)
);

CREATE TABLE IF NOT EXISTS job_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_type TEXT NOT NULL,
  job_status TEXT DEFAULT 'pending',
  payload TEXT NOT NULL,
  date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cache_oku_feed (
  feed_type TEXT,
  build_date TIMESTAMP,
  json JSON,
  PRIMARY KEY (feed_type, build_date)
);

CREATE TABLE IF NOT EXISTS cache_goodreads_book (
  isbn TEXT NOT NULL PRIMARY KEY,
  json JSON,
  date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_status_read_after_insert
AFTER INSERT ON book_event
FOR EACH ROW
WHEN NEW.event_type IN ('read', 'not-read', 'reading')
BEGIN
  UPDATE book
  SET
    status_read = NEW.event_type,
    date_updated = CURRENT_TIMESTAMP,
    date_last_read_event = NEW.date_created
  WHERE id = NEW.book_id
    AND NEW.date_created = (SELECT MAX(date_created) FROM book_event WHERE book_id = NEW.book_id);
END;

CREATE TRIGGER IF NOT EXISTS update_status_owned_after_insert
AFTER INSERT ON book_event
FOR EACH ROW
WHEN NEW.event_type IN ('owned', 'not-owned', 'on-loan', 'wanted')
BEGIN
  UPDATE book
  SET
    status_owned = NEW.event_type,
    date_updated = CURRENT_TIMESTAMP,
    date_last_owned_event = NEW.date_created
  WHERE id = NEW.book_id
    AND NEW.date_created = (SELECT MAX(date_created) FROM book_event WHERE book_id = NEW.book_id);
END;

CREATE TRIGGER IF NOT EXISTS update_status_read_after_update
AFTER UPDATE ON book_event
FOR EACH ROW
WHEN NEW.event_type IN ('read', 'not-read', 'reading')
BEGIN
  UPDATE book
  SET
    status_read = NEW.event_type,
    date_updated = CURRENT_TIMESTAMP,
    date_last_read_event = NEW.date_created
  WHERE id = NEW.book_id
    AND NEW.date_created = (SELECT MAX(date_created) FROM book_event WHERE book_id = NEW.book_id);
END;

CREATE TRIGGER IF NOT EXISTS update_status_owned_after_update
AFTER UPDATE ON book_event
FOR EACH ROW
WHEN NEW.event_type IN ('owned', 'not-owned', 'on-loan', 'wanted')
BEGIN
  UPDATE book
  SET
    status_owned = NEW.event_type,
    date_updated = CURRENT_TIMESTAMP,
    date_last_owned_event = NEW.date_created
  WHERE id = NEW.book_id
    AND NEW.date_created = (SELECT MAX(date_created) FROM book_event WHERE book_id = NEW.book_id);
END;

CREATE TRIGGER IF NOT EXISTS update_status_read_after_delete
AFTER DELETE ON book_event
FOR EACH ROW
WHEN OLD.event_type IN ('read', 'not-read', 'reading')
BEGIN
  UPDATE book
  SET
    status_read = (
      SELECT event_type
      FROM book_event
      WHERE book_id = OLD.book_id
        AND event_type IN ('read', 'not-read', 'reading')
      ORDER BY date_created DESC
      LIMIT 1
    ),
    date_updated = CURRENT_TIMESTAMP,
    date_last_read_event = (
      SELECT date_created
      FROM book_event
      WHERE book_id = OLD.book_id
        AND event_type IN ('read', 'not-read', 'reading')
      ORDER BY date_created DESC
      LIMIT 1
    )
  WHERE id = OLD.book_id;
END;

CREATE TRIGGER IF NOT EXISTS update_status_owned_after_delete
AFTER DELETE ON book_event
FOR EACH ROW
WHEN OLD.event_type IN ('owned', 'not-owned', 'on-loan', 'wanted')
BEGIN
  UPDATE book
  SET
    status_owned = (
      SELECT event_type
      FROM book_event
      WHERE book_id = OLD.book_id
        AND event_type IN ('owned', 'not-owned', 'on-loan', 'wanted')
      ORDER BY date_created DESC
      LIMIT 1
    ),
    date_updated = CURRENT_TIMESTAMP,
    date_last_owned_event = (
      SELECT date_created
      FROM book_event
      WHERE book_id = OLD.book_id
        AND event_type IN ('owned', 'not-owned', 'on-loan', 'wanted')
      ORDER BY date_created DESC
      LIMIT 1
    )
  WHERE id = OLD.book_id;
END;
