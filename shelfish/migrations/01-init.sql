CREATE TABLE IF NOT EXISTS book (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  author TEXT,
  image_url TEXT,
  description TEXT,
  status_read TEXT DEFAULT 'not-read',
  status_owned TEXT DEFAULT 'not-owned',
  isbn TEXT UNIQUE,
  isbn13 TEXT,
  asin TEXT,
  oku_id TEXT UNIQUE,
  goodreads_id TEXT,
  amazon_id TEXT,
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
