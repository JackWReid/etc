package model

import (
	"database/sql"
	"fmt"
	"math/rand"
	"time"
	"strconv"
	"shelfish/services"
)

type OwnedStatus string

const (
	Owned    OwnedStatus = "owned"
	NotOwned OwnedStatus = "not-owned"
	OnLoan   OwnedStatus = "on-loan"
	Wanted   OwnedStatus = "wanted"
)

type ReadStatus string

const (
	Read    ReadStatus = "read"
	NotRead ReadStatus = "not-read"
	Reading ReadStatus = "reading"
)

type StatusFilter struct {
	OwnedStatus *OwnedStatus
	ReadStatus  *ReadStatus
}

type BookEvent struct {
	EventType string
	EventDate time.Time
	Book DbBook
}

type DisplayBookEvent struct {
	EventType string
	EventDate string
	Book DisplayBook
}

type DbBook struct {
	ID                 int64       `json:"id"`
	Title              string      `json:"title"`
	Author             *string     `json:"author,omitempty"`
	ImageURL           *string     `json:"image_url,omitempty"`
	Description        *string     `json:"description,omitempty"`
	StatusRead         ReadStatus  `json:"status_read"`
	StatusOwned        OwnedStatus `json:"status_owned"`
	ISBN               *string     `json:"isbn,omitempty"`
	ISBN13             *string     `json:"isbn13,omitempty"`
	ASIN               *string     `json:"asin,omitempty"`
	OkuID              *string     `json:"oku_id,omitempty"`
	GoodreadsID        *string     `json:"goodreads_id,omitempty"`
	AmazonID           *string     `json:"amazon_id,omitempty"`
	DatePublished      time.Time   `json:"date_published"`
	DateLastReadEvent  *time.Time  `json:"date_last_read_event,omitempty"`
	DateLastOwnedEvent *time.Time  `json:"date_last_owned_event,omitempty"`
	DateCreated        time.Time   `json:"date_created"`
	DateUpdated        time.Time   `json:"date_updated"`
}

type DisplayBook struct {
	ID                 string     `json:"id"`
	Title              string     `json:"title"`
	Author             string     `json:"author"`
	ImageURL           string     `json:"image_url"`
	Description        string     `json:"description"`
	StatusRead         string     `json:"status_read"`
	StatusOwned        string     `json:"status_owned"`
	ISBN               string     `json:"isbn"`
	ISBN13             string     `json:"isbn13"`
	ASIN               string     `json:"asin"`
	OkuID              string     `json:"oku_id"`
	OkuURL             string     `json:"oku_url"`
	GoodreadsID        string     `json:"goodreads_id"`
	GoodreadsURL       string     `json:"goodreads_url"`
	AmazonID           string     `json:"amazon_id"`
	AmazonURL          string     `json:"amazon_url"`
	DatePublished      string     `json:"date_published"`
	DateLastReadEvent  string     `json:"date_last_read_event,omitempty"`
	DateLastOwnedEvent string     `json:"date_last_owned_event,omitempty"`
	DateCreated        string     `json:"date_created"`
	DateUpdated        string     `json:"date_updated"`
}

type SubmissionBook struct {
	ID           string
 	Title        string
  Author       string
  Description  *string
  Owned        string
  ISBN         *string
  ISBN13       *string
  ASIN         *string
  OkuId        *string
  GoodreadsId  *string
  AmazonId     *string
}

func stringOrEmpty(s *string, prefix string) string {
	if s == nil {
		return ""
	}

	return prefix + *s
}

func randomFallbackCover(imageURL string) string {
	if imageURL == "" {
		random := fmt.Sprint(1 + rand.Intn(3))
		return "/static/placeholders/book-cover-" + random + ".png"
	}

	return imageURL
}

func dateToString(date time.Time) string {
  return date.Format(time.RFC3339)
}

func optDateToString(date *time.Time) string {
	if date == nil {
		return ""
	}

	return dateToString(*date)
}

func ToDisplayBook(book DbBook) DisplayBook {
	return DisplayBook{
		ID:                 strconv.FormatInt(book.ID, 10),
		Title:              book.Title,
		Author:             stringOrEmpty(book.Author, ""),
		ImageURL:           randomFallbackCover(stringOrEmpty(book.ImageURL, "")),
		Description:        stringOrEmpty(book.Description, ""),
		StatusRead:         string(book.StatusRead),
		StatusOwned:        string(book.StatusOwned),
		ISBN:               stringOrEmpty(book.ISBN, ""),
		ISBN13:             stringOrEmpty(book.ISBN13, ""),
		ASIN:               stringOrEmpty(book.ASIN, ""),
		OkuID:              stringOrEmpty(book.OkuID, ""),
		OkuURL:             stringOrEmpty(book.OkuID, "https://oku.club/book/"),
		GoodreadsID:        stringOrEmpty(book.GoodreadsID, ""),
		GoodreadsURL:       stringOrEmpty(book.GoodreadsID, "https://www.goodreads.com/book/show/"),
		AmazonID:           stringOrEmpty(book.AmazonID, ""),
		AmazonURL:          stringOrEmpty(book.AmazonID, "https://www.amazon.com/dp/"),
		DatePublished:      dateToString(book.DatePublished),
		DateLastReadEvent:  optDateToString(book.DateLastReadEvent),
		DateLastOwnedEvent: optDateToString(book.DateLastOwnedEvent),
		DateCreated:        dateToString(book.DateCreated),
		DateUpdated:        dateToString(book.DateUpdated),
	}
}

func ToDisplayBookEvent (event BookEvent) DisplayBookEvent {
	return DisplayBookEvent{
		EventType: event.EventType,
		EventDate: dateToString(event.EventDate),
		Book: ToDisplayBook(event.Book),
	}
}

func buildStatusFilter (statusFilter StatusFilter) string {
	var query string

	if statusFilter.ReadStatus != nil && statusFilter.OwnedStatus != nil {
		return fmt.Sprintf("WHERE status_read = %s AND status_owned = %s", statusFilter.ReadStatus, statusFilter.OwnedStatus)
	}

	if statusFilter.ReadStatus != nil {
		return fmt.Sprintf("WHERE status_read = %s", statusFilter.ReadStatus)
	}

	if statusFilter.OwnedStatus != nil {
		return fmt.Sprintf("WHERE status_owned = %s", statusFilter.OwnedStatus)
	}

	return query
}

func scanDbBook(scanner interface {
	Scan(dest ...interface{}) error
}) (DbBook, error) {
	var book DbBook
	err := scanner.Scan(
		&book.ID,
		&book.Title,
		&book.Author,
		&book.ImageURL,
		&book.Description,
		&book.StatusRead,
		&book.StatusOwned,
		&book.ISBN,
		&book.ISBN13,
		&book.ASIN,
		&book.OkuID,
		&book.GoodreadsID,
		&book.AmazonID,
		&book.DatePublished,
		&book.DateLastReadEvent,
		&book.DateLastOwnedEvent,
		&book.DateCreated,
		&book.DateUpdated,
	)
	return book, err
}

func scanDbBookEvent(scanner interface {
	Scan(dest ...interface{}) error
}) (BookEvent, error) {
	var event BookEvent
	err := scanner.Scan(
		&event.EventType,
		&event.EventDate,
		&event.Book.ID,
		&event.Book.Title,
		&event.Book.Author,
		&event.Book.ImageURL,
		&event.Book.Description,
		&event.Book.StatusRead,
		&event.Book.StatusOwned,
		&event.Book.ISBN,
		&event.Book.ISBN13,
		&event.Book.ASIN,
		&event.Book.OkuID,
		&event.Book.GoodreadsID,
		&event.Book.AmazonID,
		&event.Book.DatePublished,
		&event.Book.DateLastReadEvent,
		&event.Book.DateLastOwnedEvent,
		&event.Book.DateCreated,
		&event.Book.DateUpdated,
	)
	return event, err
}

func GetBooksByAuthor(db *sql.DB, queryFilter QueryFilter, author string) ([]DbBook, error) {
	var books []DbBook

	filterQuery := buildQueryFilter(queryFilter)
	query := "SELECT * FROM book WHERE author LIKE ?" + filterQuery
	rows, err := db.Query(query, author)
	if err != nil {
		return books, err
	}
	defer rows.Close()

	for rows.Next() {
		book, err := scanDbBook(rows)
		if err != nil {
			return books, err
		}
		books = append(books, book)
	}

	return books, nil
}

func GetBooksByTitle(db *sql.DB, queryFilter QueryFilter, title string) ([]DbBook, error) {
	var books []DbBook

	filterQuery := buildQueryFilter(queryFilter)
	query := "SELECT * FROM book WHERE title LIKE ?" + filterQuery
	rows, err := db.Query(query, title)
	if err != nil {
		return books, err
	}
	defer rows.Close()

	for rows.Next() {
		book, err := scanDbBook(rows)
		if err != nil {
			return books, err
		}
		books = append(books, book)
	}

	return books, nil
}

func GetBookById(db *sql.DB, id int64) (DbBook, error) {
	row := db.QueryRow("SELECT * FROM book WHERE id = ?", id)
	book, err := scanDbBook(row)

	if err != nil {
		return book, err
	}

	return book, nil
}

func GetBooksByReadStatus(db *sql.DB, queryFilter QueryFilter, status ReadStatus) ([]DbBook, error) {
	var books []DbBook

	filterQuery := buildQueryFilter(queryFilter)
	query := "SELECT * FROM book WHERE status_read = ?" + filterQuery
	rows, err := db.Query(query, status)
	if err != nil {
		return books, err
	}
	defer rows.Close()

	for rows.Next() {
		book, err := scanDbBook(rows)
		if err != nil {
			return books, err
		}
		books = append(books, book)
	}

	return books, nil
}

type EditBook struct {
}

func EditBookById(db *sql.DB, bookId string, editBook SubmissionBook) (DbBook, error) {
  query := `UPDATE book SET
    title = ?,
    author = ?,
    description = ?,
    status_owned = ?,
    isbn = ?,
    isbn13 = ?,
    asin = ?,
    oku_id = ?,
    goodreads_id = ?,
    amazon_id = ?,
    date_updated = ?
  WHERE id = ?`

  _, err := db.Exec(query,
    editBook.Title,
    editBook.Author,
    editBook.Description,
    editBook.Owned,
    editBook.ISBN,
    editBook.ISBN13,
    editBook.ASIN,
    editBook.OkuId,
    editBook.GoodreadsId,
    editBook.AmazonId,
    time.Now(),
    bookId)

  if err != nil {
    return DbBook{}, err
  }

  // Fetch and return the updated book
  intId, _ := strconv.ParseInt(bookId, 10, 64)
  updatedBook, err := GetBookById(db, intId)
  if err != nil {
    return DbBook{}, err
  }

  return updatedBook, nil
}

func GetBookEvents(db *sql.DB, statusFilter StatusFilter, queryFilter QueryFilter) ([]BookEvent, error) {
	statusQuery := buildStatusFilter(statusFilter)
	filterQuery := buildQueryFilter(queryFilter)
	events := make([]BookEvent, 0)

	query := `
		SELECT
			be.event_type,
			be.date_created AS event_date,
			b.id,
			b.title,
			b.author,
			b.image_url,
			b.description,
			b.status_read,
			b.status_owned,
			b.isbn,
			b.isbn13,
			b.asin,
			b.oku_id,
			b.goodreads_id,
			b.amazon_id,
			b.date_published,
			b.date_last_read_event,
			b.date_last_owned_event,
			b.date_created,
			b.date_updated
		FROM book_event AS be
		JOIN book AS b ON be.book_id = b.id
	` + statusQuery + filterQuery
	rows, err := db.Query(query)

	if err != nil {
		return events, err
	}
	defer rows.Close()

	for rows.Next() {
		event, err := scanDbBookEvent(rows)
		if err != nil {
			return events, err
		}
		events = append(events, event)
	}

	return events, nil
}

func GetBookByOkuId(db *sql.DB, okuId string) (DbBook, error) {
	row := db.QueryRow("SELECT * FROM book WHERE oku_id = ?", okuId)
	book, err := scanDbBook(row)

	if err != nil {
		return book, err
	}

	return book, nil
}

func InsertOkuBook(db *sql.DB, ob services.OkuBook) error {
	query := `INSERT OR IGNORE INTO book (
		title,
		author,
		image_url,
		description,
		oku_id,
		date_published,
		date_created,
		date_updated
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := db.Exec(
		query,
		ob.Title,
		ob.Author,
		ob.ImageUrl,
		ob.Description,
		ob.Guid,
		ob.PubDate,
		ob.UpdateDate,
		ob.UpdateDate)

	if err != nil {
		return err
	}

	return nil
}

func InsertOkuBookEvent(db *sql.DB, be services.OkuBookEvent) error {
	b, err := GetBookByOkuId(db, be.BookGuid)

	if err != nil {
		return err
	}

	query := `INSERT OR IGNORE INTO book_event (
		event_type,
		book_id,
		date_created
	) VALUES (?, ?, ?)`

	_, err = db.Exec(
		query,
		be.EventType,
		b.ID,
		be.EventDate)

	if err != nil {
		return err
	}

	return nil
}
