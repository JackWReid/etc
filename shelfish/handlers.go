package main

import (
	"fmt"
	"net/http"
	"strconv"

	"shelfish/model"
	"shelfish/templates"
	"shelfish/services"

	"github.com/gorilla/mux"
)

type PageData struct {
	Title   string
	Message string
}

func (app *App) HomeHandler(w http.ResponseWriter, r *http.Request) {
	book_events, err := model.GetBookEvents(app.DB, model.StatusFilter{}, model.QueryFilter{
		SortBy: "event_date",
		Order:  "DESC",
		Limit:  "500",
	})

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	displayBookEvents := make([]model.DisplayBookEvent, len(book_events))
	for i, book_event := range book_events {
		displayBookEvents[i] = model.ToDisplayBookEvent(book_event)
	}

	component := templates.Home("Home", displayBookEvents)
	component.Render(r.Context(), w)
}

func (app *App) ListHandler(w http.ResponseWriter, r *http.Request) {
	books, err := model.GetBooksByReadStatus(app.DB, model.QueryFilter{
		SortBy: "date_created",
		Order:  "DESC",
		Limit:  "500",
	}, "read")

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	displayBooks := make([]model.DisplayBook, len(books))
	for i, book := range books {
		displayBooks[i] = model.ToDisplayBook(book)
	}

	component := templates.Gallery("Gallery", displayBooks)
	component.Render(r.Context(), w)
}

func (app *App) AddPageHandler(w http.ResponseWriter, r *http.Request) {
	component := templates.AddPage("Add Book")
	component.Render(r.Context(), w)
}

func (app *App) SearchResultsPageHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("SearchResultsPageHandler")
	var goodreadsBook services.GoodreadsScrapeBook
	var err error

	title := r.FormValue("title")
	author := r.FormValue("author")
	isbn := r.FormValue("isbn")

	if title == "" && author == "" && isbn == "" {
		// redirect to home
		panic("No search query provided")
	}

	if isbn != "" {
		goodreadsBook, err = services.ScrapeGoodreadsISBN(isbn)
	} else if title != "" || author != "" {
		goodreadsBook, err = services.ScrapeGoodreadsByTitleAuthor(title, author)
	}

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	component := templates.SearchResultsPage("Search results", goodreadsBook)
	component.Render(r.Context(), w)
}

func (app *App) JobsHandler(w http.ResponseWriter, r *http.Request) {
	jobs, err := model.GetJobQueue(app.DB)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	component := templates.Jobs("Jobs", jobs)
	component.Render(r.Context(), w)
}

func (app *App) BookDetailHandler(w http.ResponseWriter, r *http.Request) {
	bookId := mux.Vars(r)["id"]
	bookIdInt64, err := strconv.ParseInt(bookId, 10, 64)

	if err != nil {
		http.Error(w, "Invalid book ID", http.StatusBadRequest)
		return
	}

	book, err := model.GetBookById(app.DB, bookIdInt64)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	displayBook := model.ToDisplayBook(book)

	component := templates.BookDetail(displayBook)
	component.Render(r.Context(), w)
}

func (app *App) BookEditHandler(w http.ResponseWriter, r *http.Request) {
	bookId := mux.Vars(r)["id"]
	bookIdInt64, err := strconv.ParseInt(bookId, 10, 64)

	if err != nil {
		http.Error(w, "Invalid book ID", http.StatusBadRequest)
		return
	}

	book, err := model.GetBookById(app.DB, bookIdInt64)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	displayBook := model.ToDisplayBook(book)

	component := templates.BookEdit(displayBook)
	component.Render(r.Context(), w)
}

func (app *App) BookUpdateHandler(w http.ResponseWriter, r *http.Request) {
	bookId := mux.Vars(r)["id"]
	bookIdInt64, err := strconv.ParseInt(bookId, 10, 64)

	if err != nil {
		http.Error(w, "Invalid book ID", http.StatusBadRequest)
		return
	}

	_, err = model.GetBookById(app.DB, bookIdInt64)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	submittedBook := model.SubmissionBook{}
	submittedBook.ID = bookId
	submittedBook.Title = r.FormValue("title")
	submittedBook.Author = r.FormValue("author")

	if r.FormValue("description") != "" {
		description := r.FormValue("description")
		submittedBook.Description = &description
	}

	if r.FormValue("owned") == "" {
		submittedBook.Owned = "not-owned"
	} else {
		submittedBook.Owned = "owned"
	}

	if r.FormValue("isbn") != "" {
		isbn := r.FormValue("isbn")
		submittedBook.ISBN = &isbn
	}

	if r.FormValue("isbn13") != "" {
		isbn13 := r.FormValue("isbn13")
		submittedBook.ISBN13 = &isbn13
	}

	if r.FormValue("asin") != "" {
		asin := r.FormValue("asin")
		submittedBook.ASIN = &asin
	}

	if r.FormValue("oku_id") != "" {
		oku_id := r.FormValue("oku_id")
		submittedBook.OkuId = &oku_id
	}

	if r.FormValue("goodreads_id") != "" {
		goodreads_id := r.FormValue("goodreads_id")
		submittedBook.GoodreadsId = &goodreads_id
	}

	if r.FormValue("amazon_id") != "" {
		amazon_id := r.FormValue("amazon_id")
		submittedBook.AmazonId = &amazon_id
	}

	_, err = model.EditBookById(app.DB, bookId, submittedBook)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// onSuccess, redirect back to the edited book
	http.Redirect(w, r, fmt.Sprintf("/book/%s", bookId), http.StatusFound)
}
