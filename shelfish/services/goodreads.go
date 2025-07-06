package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type GoodreadsScrapeBook struct {
	ID            string
	Title         string
	Author        string
	ImageURL      string
	Description   string
	ISBN          string
	ISBN13        string
	ASIN          string `json:",omitempty"`
	DatePublished time.Time
	Publisher     string `json:",omitempty"`
	Genres        []string
	AmazonID      string
}

func ScrapeGoodreadsByTitleAuthor(title string, author string) (GoodreadsScrapeBook, error) {
	qTitle := strings.ToLower(strings.ReplaceAll(title, " ", "+"))
	qAuthor := strings.ToLower(strings.ReplaceAll(author, " ", "+"))
	searchQuery := fmt.Sprintf("?q=%s+%s", qTitle, qAuthor)

	searchURL := fmt.Sprintf("https://www.goodreads.com/search%s", searchQuery)
	resp, err := http.Get(searchURL)
	if err != nil {
		return GoodreadsScrapeBook{}, err
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return GoodreadsScrapeBook{}, err
	}

	// TODO support returning a list of results, not just the first one
	bookPathname, exists := doc.Find("[itemtype='http://schema.org/Book']").First().Find(".bookTitle").Attr("href")
	if !exists {
		return GoodreadsScrapeBook{}, fmt.Errorf("Book link not found")
	}

	bookURL := fmt.Sprintf("https://www.goodreads.com%s", bookPathname)
	return ScrapeGoodreadsBookDetail(bookURL)
}

func ScrapeGoodreadsISBN(isbn string) (GoodreadsScrapeBook, error) {
	bookURL := fmt.Sprintf("https://www.goodreads.com/search?q=%s", isbn)
	return ScrapeGoodreadsBookDetail(bookURL)
}

// Also works with ISBNs
// Example: https://www.goodreads.com/search?q=9780143128542
func ScrapeGoodreadsBookDetail(bookUrl string) (GoodreadsScrapeBook, error) {
	var err error
	defer func() {
		if r := recover(); r != nil {
			if e, ok := r.(error); ok {
				err = e
			} else {
				err = fmt.Errorf("panic occurred: %v", r)
			}
		}
	}()

	if err != nil {
		return GoodreadsScrapeBook{}, err
	}

	resp, err := http.Get(bookUrl)
	if err != nil {
		return GoodreadsScrapeBook{}, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return GoodreadsScrapeBook{}, fmt.Errorf("Failed to fetch book detail: %s", resp.Status)
	}

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return GoodreadsScrapeBook{}, err
	}

	nextDataScript := doc.Find("script#__NEXT_DATA__").Text()

	var bookPageData struct {
		Props struct {
			PageProps struct {
				ApolloState map[string]interface{} `json:"apolloState"`
				Params      struct {
					BookID string `json:"book_id"`
				} `json:"params"`
			} `json:"pageProps"`
		} `json:"props"`
	}

	err = json.Unmarshal([]byte(nextDataScript), &bookPageData)
	if err != nil {
		return GoodreadsScrapeBook{}, err
	}

	var apolloBookQuery map[string]interface{}
	for _, v := range bookPageData.Props.PageProps.ApolloState {
		if m, ok := v.(map[string]interface{}); ok {
			if m["__typename"] == "Book" {
				apolloBookQuery = m
				break
			}
		}
	}

	if apolloBookQuery == nil {
		return GoodreadsScrapeBook{}, fmt.Errorf("Book data not found")
	}

	millisFloat := apolloBookQuery["details"].(map[string]interface{})["publicationTime"].(float64)
	millis := int64(millisFloat)
	seconds := millis / 1000
	nanoseconds:= (millis % 1000) * int64(time.Millisecond)
	dateTime := time.Unix(seconds, nanoseconds)

	details, ok := apolloBookQuery["details"].(map[string]interface{})
	if !ok {
		return GoodreadsScrapeBook{}, fmt.Errorf("Book details not found")
	}
	if details["isbn"] == nil {
		return GoodreadsScrapeBook{}, fmt.Errorf("Book ISBN not found")
	}

	bookData := GoodreadsScrapeBook{
		ID:            bookPageData.Props.PageProps.Params.BookID,
		Title:         apolloBookQuery["titleComplete"].(string),
		Description:   apolloBookQuery["description"].(string),
		ImageURL:      apolloBookQuery["imageUrl"].(string),
		ISBN:          apolloBookQuery["details"].(map[string]interface{})["isbn"].(string),
		ISBN13:        apolloBookQuery["details"].(map[string]interface{})["isbn13"].(string),
		DatePublished: dateTime,
		Genres:        []string{},
		AmazonID:      "",
	}

	if asin, ok := apolloBookQuery["details"].(map[string]interface{})["asin"].(string); ok && asin != "" {
		bookData.ASIN = asin
	}

	if publisher, ok := apolloBookQuery["details"].(map[string]interface{})["publisher"].(string); ok && publisher != "" {
		bookData.Publisher = publisher
	}

	for _, genre := range apolloBookQuery["bookGenres"].([]interface{}) {
		genreName := genre.(map[string]interface{})["genre"].(map[string]interface{})["name"].(string)
		bookData.Genres = append(bookData.Genres, strings.ToLower(genreName))
	}

	links := apolloBookQuery["links({})"].(map[string]interface{})
	secondaryAffiliateLinks := links["secondaryAffiliateLinks"].([]interface{})
	if len(secondaryAffiliateLinks) > 0 {
		url := secondaryAffiliateLinks[0].(map[string]interface{})["url"].(string)
		urlParts := strings.Split(url, "/")
		if len(urlParts) > 5 {
			bookData.AmazonID = urlParts[5]
		}
	}

	return bookData, nil
}
