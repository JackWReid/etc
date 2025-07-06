package model

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"log"
	"path/filepath"
	"sort"
	"strings"

	_ "github.com/ncruces/go-sqlite3/driver"
	_ "github.com/ncruces/go-sqlite3/embed"
)

var defaultLimit = 50

type QueryFilter struct {
	SortBy string
	Order  string
	Limit  string
	Offset string
}

func buildQueryFilter(queryFilter QueryFilter) string {
	var query string

	if queryFilter.SortBy != "" {
		order := "ASC"
		if strings.ToUpper(queryFilter.Order) == "DESC" {
			order = "DESC"
		}
		query += fmt.Sprintf(" ORDER BY %s %s", queryFilter.SortBy, order)
	}

	limit := queryFilter.Limit
	if limit == "" {
		limit = fmt.Sprintf("%d", defaultLimit)
	}

	if queryFilter.Offset != "" {
		query += fmt.Sprintf(" LIMIT %s OFFSET %s", limit, queryFilter.Offset)
	} else {
		query += fmt.Sprintf(" LIMIT %s", limit)
	}

	return query
}

func StartDb() *sql.DB {
	var version string
	var err error

	db, err := sql.Open("sqlite3", "file:shelfish.db")

	if err != nil {
		log.Fatal(err)
	}

	pingErr := db.Ping()
	if pingErr != nil {
		log.Fatal(pingErr)
	}

	db.QueryRow(`SELECT sqlite_version()`).Scan(&version)
	runMigrations(db)

	return db
}

func runMigrations(db *sql.DB) {
	migrations, err := getMigrationFiles()
	if err != nil {
		log.Fatal(err)
	}

	for _, migration := range migrations {
		sql, err := readMigrationFile(migration)
		if err != nil {
			log.Fatal(err)
		}

		_, err = db.Exec(sql)
		if err != nil {
			log.Fatalf("Error executing migration %s: %v", migration, err)
		}
	}

	log.Println("All migrations completed successfully")
}

func getMigrationFiles() ([]string, error) {
	files, err := filepath.Glob("migrations/*.sql")
	if err != nil {
		return nil, err
	}
	sort.Strings(files)
	return files, nil
}

func readMigrationFile(filename string) (string, error) {
	content, err := ioutil.ReadFile(filename)
	if err != nil {
		return "", err
	}
	return string(content), nil
}
