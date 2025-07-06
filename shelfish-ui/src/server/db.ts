import { Database } from "bun:sqlite";
import {
  type DbBook,
  type GoodreadsScrapeBook,
  type OkuBookEntry,
  type OkuBookEventEntry,
  type OkuFeedName,
  type OwnedStatus,
  type ReadStatus,
} from "./types.ts";
import { dbDate, olderThanHours } from "../utils.ts";

let dbSingleton: Database | null = null;

export async function getDb(): Promise<Database> {
  if (dbSingleton !== null) {
    return dbSingleton;
  }

  const newDb = new Database("./shelfish.sqlite", { create: true });
  await runInitialSchema(newDb);
  dbSingleton = newDb;
  return newDb;
}

export async function runInitialSchema(db: Database) {
  const schemaFile = Bun.file("./migrations/00-init.sql");
  const schemaText = await schemaFile.text();
  console.log("Initializing database schema");
  db.run(schemaText);
}

export async function insertFeedCache(feedType: OkuFeedName, feed) {
  const db = await getDb();
  const insert = db.prepare(
    "INSERT OR IGNORE INTO cache_oku_feed (feed_type, build_date, json) VALUES ($feed_type, $build_date, $json)",
  );

  const result = insert.run({
    $feed_type: feedType,
    $build_date: dbDate(feed.lastBuildDate),
    $json: JSON.stringify(feed),
  });

  return result;
}

export async function getOkuFeedCache(feedType: OkuFeedName) {
  const db = await getDb();
  const query = db.prepare(
    "SELECT build_date, json FROM cache_oku_feed WHERE feed_type = $feed_type ORDER BY build_date DESC LIMIT 1",
  );

  const result = await query.get({ $feed_type: feedType });

  if (!result) {
    return null;
  }

  if (olderThanHours(24 * 7, result.build_date)) {
    return null;
  }

  return JSON.parse(result.json);
}

export async function insertOkuBookRecords(
  books: OkuBookEntry[],
): Promise<number> {
  const db = await getDb();
  const insert = db.prepare(`
    INSERT OR IGNORE
    INTO book (oku_id, title, author, image_url, description, date_published)
    VALUES ($oku_id, $title, $author, $image_url, $description, $pub_date)
    `);

  const insertBooks = db.transaction((books: OkuBookEntry[]) => {
    for (const book of books) {
      const insertBook = {
        $oku_id: book.Guid,
        $title: book.Title,
        $author: book.Author,
        $image_url: book.ImageUrl,
        $description: book.Description,
        $pub_date: dbDate(book.PubDate),
      };
      insert.run(insertBook);
    }
    return books.length;
  });

  const count = await insertBooks(books);
  return count;
}

export async function insertOkuBookEvents(
  bookEvents: OkuBookEventEntry[],
): Promise<number> {
  const db = await getDb();

  const insert = db.prepare(`
    INSERT OR IGNORE INTO
    book_event (event_type, book_id, date_created) VALUES ($event_type, $book_id, $date_created)
  `);

  const getBookId = db.prepare(`
    SELECT id FROM book WHERE oku_id = ?
  `);

  const insertBookEvents = db.transaction((events: OkuBookEventEntry[]) => {
    for (const event of events) {
      const book = getBookId.get(event.BookGuid);

      if (book) {
        const insertBookEventParams = {
          $event_type: event.EventType,
          $book_id: book.id,
          $date_created: dbDate(event.EventDate),
        };
        insert.run(insertBookEventParams);
      }
    }

    return events.length;
  });

  const count = await insertBookEvents(bookEvents);
  return count;
}

// TODO: Doesn't get the author from Goodreads
// TODO: Doesn't add the GoodreadsId
// TODO: Add triggers to update status_owned and don't update status_read incorrectly
export async function addNewBook(
  status_read: ReadStatus,
  status_owned: OwnedStatus,
  book: GoodreadsScrapeBook,
): Promise<DbBook> {
  const db = await getDb();

  const runTransaction = db.transaction(async () => {
    const insertBook = db.prepare(`
      INSERT INTO book (title, author, image_url, description, date_published, oku_id, goodreads_id, amazon_id, isbn, isbn13, asin)
      VALUES ($title, $author, $image_url, $description, $pub_date, $oku_id, $goodreads_id, $amazon_id, $isbn, $isbn13, $asin)
    `);

    const result = insertBook.run({
      $title: book.title,
      $author: book.author,
      $image_url: book.image,
      $description: book.description,
      $pub_date: book.datePublished,
      $oku_id: book.oku_id,
      $goodreads_id: book.goodreads_id,
      $amazon_id: book.amazon_id,
      $isbn: book.isbn,
      $isbn13: book.isbn13,
      $asin: book.asin,
    });

    book.id = result.lastInsertRowid;

    const insertBookReadEvent = db.prepare(`
      INSERT INTO book_event (event_type, book_id, date_created) VALUES ($event_type, $book_id, $date_created)
    `);

    insertBookReadEvent.run({
      $event_type: status_read,
      $book_id: book.id,
      $date_created: dbDate(new Date()),
    });

    const insertBookOwnedEvent = db.prepare(`
      INSERT INTO book_event (event_type, book_id, date_created) VALUES ($event_type, $book_id, $date_created)
    `);

    insertBookOwnedEvent.run({
      $event_type: status_owned,
      $book_id: book.id,
      $date_created: dbDate(new Date()),
    });

    const finalBook = await getBookById(book.id);

    return finalBook;
  });

  return await runTransaction();
}

export async function markBook(
  id: string,
  data: { status_read: ReadStatus; status_owned: OwnedStatus },
) {
  if (!id || (!data.status_read && !data.status_owned)) {
    throw new Error("Missing required fields");
  }

  if (data.status_read && data.status_owned) {
    throw new Error(
      "Cannot mark a book as both read and owned at the same time",
    );
  }

  const db = await getDb();

  if (data.status_read) {
    const query = db.prepare(
      `INSERT INTO book_event (event_type, book_id, date_created) VALUES ($event_type, $book_id, $date_created)`,
    );
    query.run({
      $event_type: data.status_read,
      $book_id: id,
      $date_created: dbDate(new Date()),
    });
  }

  if (data.status_owned) {
    const query = db.prepare(
      `INSERT INTO book_event (event_type, book_id, date_created) VALUES ($event_type, $book_id, $date_created)`,
    );
    query.run({
      $event_type: data.status_owned,
      $book_id: id,
      $date_created: dbDate(new Date()),
    });
  }

  const book = await getBookById(id);

  return book;
}

export async function getBookById(bookId: string): Promise<DbBook> {
  const db = await getDb();
  const query = db.prepare(`SELECT * FROM book WHERE id = $id`);
  const book: DbBook = await query.get({ $id: bookId });
  return book;
}

export async function getEventsByBookId(
  bookId: string,
): Promise<DbBookEvent[]> {
  const db = await getDb();
  const query = db.prepare(
    `SELECT * FROM book_event WHERE book_id = $book_id ORDER BY date_created DESC`,
  );
  const events: DbBookEvent[] = await query.all({ $book_id: bookId });
  return events;
}

export async function getBooks({
  status_owned = "",
  status_read = "",
  sort_order = "DESC",
  sort_by = "status_read",
}): Promise<DbBook[]> {
  const db = await getDb();

  const order_by =
    sort_by === "status_owned"
      ? "date_last_owned_event"
      : "date_last_read_event";

  let queryStr = `SELECT * FROM book`;
  const conditions = [];

  if (status_owned) {
    conditions.push(`status_owned = ?`);
  }
  if (status_read) {
    conditions.push(`status_read = ?`);
  }

  if (conditions.length > 0) {
    queryStr += ` WHERE ${conditions.join(" AND ")}`;
  }

  queryStr += ` ORDER BY ${order_by} ${sort_order}`;

  const query = db.prepare(queryStr);
  const books: DbBook[] = query.all(status_owned, status_read);
  return books;
}

export async function getBooksByReadStatus(
  readStatus: ReadStatus,
): Promise<DbBook[]> {
  const db = await getDb();
  const query = db.prepare(
    `SELECT * FROM book WHERE status_read = $status_read`,
  );
  const books: DbBook[] = await query.all({ $status_read: readStatus });
  return books;
}

export async function getBookStats() {
  const db = await getDb();
  const query = db.prepare(`
    SELECT
      (SELECT COUNT(*) FROM book WHERE status_read = 'read') as read,
      (SELECT COUNT(*) FROM book WHERE status_read = 'reading') as reading,
      (SELECT COUNT(*) FROM book WHERE status_read = 'not-read') as toread
  `);
  const result = await query.get();
  return result;
}

export async function getBooksBySearch(params: { search: string }) {
  const db = await getDb();
  const query = db.prepare(`
    SELECT * FROM book WHERE title LIKE $search
  `);
  const books: DbBook[] = query.all({ $search: `%${params.search}%` });
  return books;
}
