package model

import (
	"database/sql"
	"encoding/json"
	"log"
	"strconv"
  "shelfish/services"
)

type Job struct {
	ID          int64
	Type        string
	Status      string
	Payload     string
	DateCreated string
}

type BookScrapePayload struct {
	ID     int `json:"bookId"`
	Title  string
	Author string
}

type OkuSyncPayload struct {
	FeedName string `json:"feed_name"`
}

func clearJobQueue(db *sql.DB, jobType string) error {
	result, err := db.Exec("DELETE FROM job_queue WHERE job_type = ?", jobType)
	log.Print(result)
	return err
}

func GenerateJobsOkuSync(db *sql.DB, clear bool) error {
	var err error

	if clear {
		err = clearJobQueue(db, "oku_sync")
	}

	query := `
    INSERT INTO job_queue(job_type, payload)
    VALUES ('oku_sync', '{"feed_name":"read"}'),
           ('oku_sync', '{"feed_name":"not-read"}'),
           ('oku_sync', '{"feed_name":"reading"}')
	`
	_, err = db.Exec(query)
	if err != nil {
		return err
	}

	return nil
}

func GenerateJobsGoodreadsScrape(db *sql.DB, clear bool) error {
	var err error
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	if clear {
		err = clearJobQueue(db, "goodreads_scrape")
	}

	rows, err := tx.Query(`
		SELECT book.id, book.title, book.author
		FROM book
		WHERE book.isbn IS NULL
		AND NOT EXISTS (
			SELECT 1
			FROM job_queue jq
			WHERE jq.job_type = 'goodreads_scrape'
			AND jq.payload->>'bookId' = CAST(book.id AS TEXT) = book.id
		)
		ORDER BY RANDOM()
	`)
	if err != nil {
		return err
	}
	defer rows.Close()

	stmt, err := tx.Prepare(`
    INSERT INTO job_queue(job_type, payload)
    VALUES (?, ?)
	`)

	if err != nil {
		return err
	}
	defer stmt.Close()

	for rows.Next() {
		book := BookScrapePayload{}

		var authorNullable sql.NullString
		if err := rows.Scan(&book.ID, &book.Title, &authorNullable); err != nil {
			log.Print("failed to scan")
			log.Print(err)
		}
		if authorNullable.Valid {
			book.Author = authorNullable.String
		} else {
			log.Printf("author null for %s", book.Title)
			book.Author = ""
		}

		payload, err := json.Marshal(map[string]interface{}{
			"bookId": book.ID,
			"title":  book.Title,
			"author": book.Author,
		})
		if err != nil {
			return err
		}

		_, err = stmt.Exec("goodreads_scrape", payload)

		if err != nil {
			return err
		}
	}

	if err := rows.Err(); err != nil {
		return err
	}

	if err := tx.Commit(); err != nil {
		return err
	}

	return nil
}

func ScrapeGoodreadsBook(db *sql.DB, payload BookScrapePayload) error {
	goodreadsBook, err := services.ScrapeGoodreadsByTitleAuthor(payload.Title, payload.Author)

	if err != nil {
		return err
	}

	stmt, err := db.Prepare(`
    INSERT INTO cache_goodreads_book(isbn, json)
    VALUES (?, ?)
    ON CONFLICT(isbn) DO UPDATE SET
      json = excluded.json,
      date_updated = CURRENT_TIMESTAMP
  `)
	if err != nil {
		return err
	}
	defer stmt.Close()

	jsonData, err := json.Marshal(goodreadsBook)
	if err != nil {
		return err
	}

	_, err = stmt.Exec(goodreadsBook.ISBN, string(jsonData))
	if err != nil {
		return err
	}

	stmt, err = db.Prepare(`
    UPDATE book
    SET
      image_url = ?,
      description = ?,
      isbn = ?,
      isbn13 = ?,
      asin = ?,
      goodreads_id = ?,
      amazon_id = ?,
      date_published = ?
    WHERE id = ?
  `)
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec(
		goodreadsBook.ImageURL,
		goodreadsBook.Description,
		goodreadsBook.ISBN,
		goodreadsBook.ISBN13,
		goodreadsBook.ASIN,
		goodreadsBook.ID,
		goodreadsBook.AmazonID,
		goodreadsBook.DatePublished,
		payload.ID,
	)

	if err != nil {
		return err
	}

	return nil
}

func SyncOkuFeed(db *sql.DB, feedName string) error {
	feed := services.GetOkuFeed(feedName)

	for _, book := range feed.Books {
		err := InsertOkuBook(db, book)
		if err != nil {
			return err
		}
	}

	for _, event := range feed.Events {
		err := InsertOkuBookEvent(db, event)
		if err != nil {
			return err
		}
	}

	return nil
}

func ExecuteNextJob(db *sql.DB) (Job, error) {
	job := Job{}
	err := db.QueryRow(`
		SELECT id, job_type, payload
				FROM job_queue
				WHERE job_status = 'pending'
				ORDER BY date_created ASC LIMIT 1
	`).Scan(
		&job.ID,
		&job.Type,
		&job.Payload,
	)

	jobIdStr := strconv.FormatInt(job.ID, 10)

	if err != nil {
		if err == sql.ErrNoRows {
			return job, nil
		}

		log.Printf("Failed to select next job: %s", err)
		return job, err
	}

	_, err = db.Exec(`
		UPDATE job_queue
		SET job_status = 'running'
		WHERE id = ?
	`, job.ID)

	if err != nil {
		log.Printf("[%s - %s] Failed to set job running: %s", jobIdStr, job.Type, err)
		return job, err
	}

	if job.Type == "goodreads_scrape" {
		payload := BookScrapePayload{}
		err = json.Unmarshal([]byte(job.Payload), &payload)

		if err != nil {
			_, _ = db.Exec(`
				UPDATE job_queue
				SET job_status = 'failed'
				WHERE id = ?
			`, job.ID)
			log.Printf("[%s - %s] Failed to decode job payload: %s", jobIdStr, job.Type, err)
			return job, err
		}

		log.Printf("[%s - %s] Executing job: %s", jobIdStr, job.Type, payload.Title)
		err = ScrapeGoodreadsBook(db, payload)
	}

	if job.Type == "oku_sync" {
		payload := OkuSyncPayload{}
		err = json.Unmarshal([]byte(job.Payload), &payload)

		if err != nil {
			_, _ = db.Exec(`
				UPDATE job_queue
				SET job_status = 'failed'
				WHERE id = ?
			`, job.ID)
			log.Printf("[%s - %s] Failed to decode job payload: %s", jobIdStr, job.Type, err)
			return job, err
		}

		log.Printf("[%s - %s] Executing job: %s", jobIdStr, job.Type, payload.FeedName)
		err = SyncOkuFeed(db, payload.FeedName)
	}

	if err != nil {
		_, _ = db.Exec(`
			UPDATE job_queue
			SET job_status = 'failed'
			WHERE id = ?
		`, job.ID)

		log.Printf("[%s - %s] Failed to execute job: %s", jobIdStr, job.Type, err)
		return job, err
	}

	_, err = db.Exec(`
		UPDATE job_queue
		SET job_status = 'completed'
		WHERE id = ?
	`, job.ID)

	if err != nil {
		log.Printf("Failed to set job completed: %s", err)
		return job, err
	}

	log.Printf("[%s - %s] Completed job", jobIdStr, job.Type)
	return job, nil
}

func GetJobQueue(db *sql.DB) ([]Job, error) {
	rows, err := db.Query(`
		SELECT id, job_type, job_status, payload, date_created
		FROM job_queue
		ORDER BY date_created ASC
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var jobs []Job
	for rows.Next() {
		var job Job
		err := rows.Scan(&job.ID, &job.Type, &job.Status, &job.Payload, &job.DateCreated)
		if err != nil {
			return nil, err
		}
		jobs = append(jobs, job)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return jobs, nil
}

// TODO accept job_type and job_status as arguments
func GetJobQueueCount(db *sql.DB) int {
	var count int
	err := db.QueryRow(`
		SELECT COUNT(*) as count
		FROM job_queue
		WHERE job_status = 'pending' OR job_status = 'running'
 `).Scan(&count)
	if err != nil {
		log.Printf("Error getting job queue count: %v", err)
		return 0
	}
	return count
}
