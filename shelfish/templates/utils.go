package templates

import (
	"time"
	"github.com/dustin/go-humanize"
)

func DateStringToRelative(dateString string) string {
	date, _ := time.Parse(time.RFC3339, dateString)
	return humanize.Time(date)
}
