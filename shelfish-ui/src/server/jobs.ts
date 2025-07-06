import { getDb } from "./db";
import { scrapeGoodreadsByTitleAuthor } from "./scraping.ts";

const jobRunnerMap = {
  goodreads_scrape: scrapeGoodreads,
};

export async function generateIdentifierJobs() {
  const db = await getDb();
  const delQuery = db.prepare(
    `DELETE FROM job_queue WHERE job_type = 'goodreads_scrape'`,
  );
  delQuery.run();

  const query = db.prepare(`
    SELECT id, title, author
    FROM book
    WHERE isbn IS NULL
    ORDER BY RANDOM()
  `);
  const books = query.all();

  const insertJob = db.prepare(`
    INSERT INTO job_queue(job_type, payload)
    VALUES ($job_type, $payload)
    `);
  for (const book of books) {
    const payload = JSON.stringify({
      bookId: book.id,
      title: book.title,
      author: book.author,
    });
    insertJob.run({
      $job_type: "goodreads_scrape",
      $payload: payload,
    });
  }
}

async function scrapeGoodreads(payloadRaw: string) {
  const payload = JSON.parse(payloadRaw);
  const scrapeResult = await scrapeGoodreadsByTitleAuthor(payload);

  if (!scrapeResult.isbn) {
    console.warn(
      `Failed to find ISBN for ${payload.title} by ${payload.author}`,
    );
    return;
  }

  const db = await getDb();
  const cacheQuery = db.prepare(`
    INSERT INTO cache_goodreads_book(isbn, json)
    VALUES ($isbn, $json)
    ON CONFLICT(isbn) DO UPDATE SET
      json = excluded.json,
      date_updated = CURRENT_TIMESTAMP
    `);
  cacheQuery.run({
    $isbn: scrapeResult.isbn,
    $json: JSON.stringify(scrapeResult),
  });

  const bookQuery = db.prepare(`
    UPDATE book
    SET
      image_url = $image_url,
      description = $description,
      isbn = $isbn,
      isbn13 = $isbn13,
      asin = $asin,
      goodreads_id = $goodreads_id,
      amazon_id = $amazon_id,
      date_published = $date_published
    WHERE id = $id
    `);
  bookQuery.run({
    $id: payload.bookId,
    $image_url: scrapeResult.image,
    $description: scrapeResult.description,
    $isbn: scrapeResult.isbn,
    $isbn13: scrapeResult.isbn13,
    $asin: scrapeResult.asin,
    $goodreads_id: scrapeResult.id,
    $amazon_id: scrapeResult.amazonId,
    $date_published: scrapeResult.datePublished,
  });

  return scrapeResult;
}

export async function executeNextJob() {
  const db = await getDb();
  const query = db.prepare(`
    SELECT id, job_type, payload
    FROM job_queue
    WHERE job_status = 'pending'
    ORDER BY date_created ASC LIMIT 1
  `);

  const queueResult = await query.get();

  if (!queueResult) {
    return null;
  }

  const updateQuery = db.prepare(
    "UPDATE job_queue SET job_status = 'running' WHERE id = $id",
  );
  await updateQuery.run({ $id: queueResult.id });

  let jobResult;
  try {
    jobResult = await jobRunnerMap[queueResult.job_type](queueResult.payload);
  } catch (error) {
    console.error(error);
    const failureQuery = db.prepare(
      "UPDATE job_queue SET job_status = 'failure' WHERE id = $id",
    );
    await failureQuery.run({ $id: queueResult.id });
    return { id: queueResult.id, status: "failure", error };
  }

  const successQuery = db.prepare(
    "UPDATE job_queue SET job_status = 'success' WHERE id = $id",
  );
  await successQuery.run({ $id: queueResult.id });

  return { id: queueResult.id, status: "success", result: jobResult };
}

export async function getJobList() {
  const db = await getDb();
  const query = db.prepare(`
    SELECT id, job_type, job_status, payload, date_created
    FROM job_queue
    ORDER BY date_created ASC
  `);
  return query.all();
}

export async function getJobQueueCount() {
  const db = await getDb();
  const query = db.prepare(`
    SELECT COUNT(*) as count
    FROM job_queue
    WHERE job_status = 'pending' OR job_status = 'running'
  `);
  return query.get().count;
}
