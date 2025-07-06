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
