import { compareAsc } from "date-fns";

export function bookToSeachParams({ title, author }): string {
  const qTitle = title.toLowerCase().replace(/ /g, "+");
  const qAuthor = author.toLowerCase().replace(/ /g, "+");
  return `?q=${qTitle}+${qAuthor}`;
}

export function randomNumberBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

export function randomCoverPlaceHolder() {
  const random = randomNumberBetween(1, 3);
  return `/placeholders/book-cover-${random}.png`;
}

export function titleCase(str: string): string {
  return str
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function stripHtml(html: string): string {
  return html.replace(/<[^>]*>?/gm, "");
}

export function dbDate(date) {
  let dateClass;
  if (date instanceof Date) {
    dateClass = date;
  } else if (typeof date === "number") {
    dateClass = new Date(date);
  } else if (typeof date === "string") {
    const dateRegex = /^(\d{2})\/(\d{2})\/(\d{4}) (\d{2}):(\d{2}):(\d{2})$/;
    const match = date.match(dateRegex);
    if (match) {
      const [_, day, month, year, hour, minute, second] = match;
      dateClass = new Date(
        `${year}-${month}-${day}T${hour}:${minute}:${second}Z`,
      );
    } else {
      dateClass = new Date(date);
    }
  } else {
    throw new Error("Unable to standardize date");
  }

  const year = dateClass.getUTCFullYear();
  const month = String(dateClass.getUTCMonth() + 1).padStart(2, "0");
  const day = String(dateClass.getUTCDate()).padStart(2, "0");
  const hour = String(dateClass.getUTCHours()).padStart(2, "0");
  const minute = String(dateClass.getUTCMinutes()).padStart(2, "0");
  const second = String(dateClass.getUTCSeconds()).padStart(2, "0");

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

export function displayDate(dbDate: string) {
  const date = new Date(dbDate);
  const day = date.getDate();
  const month = date.toLocaleString("default", { month: "short" });
  const year = date.getFullYear().toString().slice(-2);
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");

  const daySuffix = (day) => {
    if (day > 3 && day < 21) return "th";
    switch (day % 10) {
      case 1:
        return "st";
      case 2:
        return "nd";
      case 3:
        return "rd";
      default:
        return "th";
    }
  };

  return `${day}${daySuffix(day)} ${month} '${year}, ${hours}:${minutes}`;
}

export function olderThanHours(hours: number, dateStr: string | Date): boolean {
  const dateClass = new Date(dateStr);
  const xHoursAgo = new Date(new Date().getTime() - hours * 60 * 60 * 1000);
  const diff = compareAsc(dateClass, xHoursAgo);

  if (diff !== 1) {
    return true;
  }

  return false;
}
