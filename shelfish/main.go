package main

import (
	"database/sql"
	"log"
	"net/http"
	"shelfish/model"
	"time"
	"github.com/gorilla/mux"
	"github.com/MadAppGang/httplog"
)

type App struct {
	DB *sql.DB
}

func main() {
	db := model.StartDb()
	app := &App{DB: db}

	r := mux.NewRouter()

	r.HandleFunc("/", app.HomeHandler)
  r.HandleFunc("/list", app.ListHandler)

  r.HandleFunc("/add", app.AddPageHandler)
  r.HandleFunc("/search", app.SearchResultsPageHandler).Methods("POST")
	r.HandleFunc("/jobs", app.JobsHandler)

	r.HandleFunc("/book/{id:[0-9]+}", app.BookDetailHandler)
	r.HandleFunc("/book/{id:[0-9]+}/edit", app.BookEditHandler).Methods("GET")
	r.HandleFunc("/book/{id:[0-9]+}/edit", app.BookUpdateHandler).Methods("POST")

	fs := http.FileServer(http.Dir("./static/"))
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", fs))
	r.Use(httplog.LoggerWithFormatter(httplog.DefaultLogFormatterWithResponseHeader))

	go func() {
		log.Println("Starting server on http://127.0.0.1:8080")
		if err := http.ListenAndServe(":8080", r); err != nil {
			log.Fatal("ListenAndServe error: ", err)
		}
	}()

	model.GenerateJobsOkuSync(db, true)
	model.GenerateJobsGoodreadsScrape(db, true)

	go func() {
		for {
			_, _ := model.ExecuteNextJob(db)
			time.Sleep(1 * time.Second)
		}
	}()

	// Keep the main goroutine running
	select {}
}
