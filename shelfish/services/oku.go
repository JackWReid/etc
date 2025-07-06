package services

import (
	"log"
	"strings"
	"time"

	"github.com/mmcdole/gofeed"
)

type OkuFeedPull struct {
	Date   time.Time
	Raw    []OkuRawFeedEntry
	Books  []OkuBook
	Events []OkuBookEvent
}

type OkuRawFeedEntry struct {
	Creator   string
	Title     string
	Link      string
	PubDate   string
	Enclosure struct {
		Length string
		Type   string
		URL    string
	}
	DCCreator      string `json:"dc:creator"`
	Content        string
	ContentSnippet string
	GUID           string
	IsoDate        string
}

type OkuBook struct {
	Guid        string
	Title       string
	Author      string
	ImageUrl    string
	Description string
	PubDate     time.Time
	UpdateDate  time.Time
}

type OkuBookEvent struct {
	EventType string
	BookGuid  string
	EventDate string
}

var OkuReadUrl string = "https://oku.club/rss/collection/zQtTo"
var OkuToreadUrl string = "https://oku.club/rss/collection/JSKHS"
var OkuReadingUrl string = "https://oku.club/rss/collection/2f67M"

var urlMap = map[string]string{
	"reading":   OkuReadingUrl,
	"not-read":  OkuToreadUrl,
	"read":      OkuReadUrl,
}

func GetOkuFeed(readStatus string) OkuFeedPull {
	var feed OkuFeedPull
	feed.Raw = getRawOkuFeed(readStatus)
	feed.Books = transformOkuFeedToBookEntries(feed.Raw)
	feed.Events = transformOkuFeedToBookEvents(feed.Raw, readStatus)
	feed.Date = time.Now()
	return feed
}

func getRawOkuFeed(collection string) []OkuRawFeedEntry {
	var resItems []OkuRawFeedEntry
	fp := gofeed.NewParser()
	feed, err := fp.ParseURL(urlMap[collection])

	if err != nil {
		log.Print(err)
	}

	for _, feedEvent := range feed.Items {
		var enclosure struct {
			Length string
			Type   string
			URL    string
		}
		if len(feedEvent.Enclosures) > 0 {
			enclosure.Length = feedEvent.Enclosures[0].Length
			enclosure.Type = feedEvent.Enclosures[0].Type
			enclosure.URL = feedEvent.Enclosures[0].URL
		}

		if feedEvent.Author == nil {
			log.Println("Skipping event with no author")
			continue
		}

		okuEvent := OkuRawFeedEntry{
			Creator:        feedEvent.Author.Name,
			Title:          feedEvent.Title,
			Link:           feedEvent.Link,
			PubDate:        feedEvent.Published,
			Enclosure:      enclosure,
			DCCreator:      feedEvent.Extensions["dc"]["creator"][0].Value,
			Content:        feedEvent.Content,
			ContentSnippet: feedEvent.Description,
			GUID:           feedEvent.GUID,
			IsoDate:        feedEvent.PublishedParsed.Format("2006-01-02"),
		}

		resItems = append(resItems, okuEvent)
	}

	return resItems
}

func transformOkuFeedToBookEntries(feed []OkuRawFeedEntry) []OkuBook {
	var bookItems []OkuBook
	for _, feedEvent := range feed {
		pubDate, _ := time.Parse(time.RFC1123Z, feedEvent.PubDate)
		updateDate, _ := time.Parse(time.RFC1123Z, feedEvent.IsoDate)
		book := OkuBook{
			Guid:        transformOkuGuidToBookGuid(feedEvent.GUID),
			Title:       feedEvent.Title,
			Author:      feedEvent.DCCreator,
			ImageUrl:    feedEvent.Enclosure.URL,
			Description: feedEvent.ContentSnippet,
			PubDate:     pubDate,
			UpdateDate:  updateDate,
		}
		bookItems = append(bookItems, book)
	}

	return bookItems
}

func transformOkuFeedToBookEvents(feed []OkuRawFeedEntry, eventType string) []OkuBookEvent {
	var eventEntries []OkuBookEvent
	for _, feedEvent := range feed {
		event := OkuBookEvent{
			EventType: eventType,
			BookGuid:  transformOkuGuidToBookGuid(feedEvent.GUID),
			EventDate: feedEvent.IsoDate,
		}
		eventEntries = append(eventEntries, event)
	}
	return eventEntries
}

func transformOkuGuidToBookGuid(okuGuid string) string {
	return strings.Replace(okuGuid, "https://oku.club/book/", "", 1)
}
