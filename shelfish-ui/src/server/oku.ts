import { Database } from "bun:sqlite";
import Parser from "rss-parser";

import {
  type OkuFeedName,
  type OkuFeedPull,
  type OkuBookEntry,
  type OkuBookEventEntry,
  type OkuRawFeedEntry,
} from "./types.ts";

import { getDb, getOkuFeedCache, insertFeedCache } from "./db.ts";
import { dbDate } from "../utils.ts";

const okuFeedUrls: Record<OkuFeedName, string> = {
  read: "https://oku.club/rss/collection/zQtTo",
  toread: "https://oku.club/rss/collection/JSKHS",
  reading: "https://oku.club/rss/collection/2f67M",
};

function transformOkuGuidToBookGuid(okuGuid: string): string {
  return okuGuid.replace("https://oku.club/book/", "");
}

export async function getOkuFeed(db: Database, feedName: OkuFeedName) {
  const cacheResult = await getOkuFeedCache(feedName);
  if (cacheResult) {
    console.log(`HIT local cache ${feedName}`);
    return cacheResult;
  }

  console.log(`MISS local cache ${feedName}`);
  const parser = new Parser();
  const feed = await parser.parseURL(okuFeedUrls[feedName]);
  await insertFeedCache(feedName, feed);
  return feed;
}

export async function getParsedOkuFeed(
  feedName: OkuFeedName,
): Promise<OkuFeedPull> {
  const db = await getDb();
  const rawOkuFeed = await getOkuFeed(db, feedName);

  // Create a list of canonical book entries
  const transformedBooks: OkuBookEntry[] = [];
  for (let item of rawOkuFeed.items) {
    const transformedItem: OkuBookEntry = okuFeedToCanonicalBook(
      rawOkuFeed.lastBuildDate,
      item,
    );
    transformedBooks.push(transformedItem);
  }

  // Create a list of book event entries
  const transformedEvents: OkuBookEventEntry[] = [];
  for (let item of rawOkuFeed.items) {
    const transformedItem: OkuBookEventEntry = okuFeedToBookEvent(
      feedName,
      item,
    );
    transformedEvents.push(transformedItem);
  }

  return {
    Date: dbDate(rawOkuFeed.lastBuildDate),
    Raw: rawOkuFeed,
    Books: transformedBooks,
    Events: transformedEvents,
  };
}

function okuFeedToCanonicalBook(
  updateDate: string,
  entry: OkuRawFeedEntry,
): OkuBookEntry {
  return {
    Guid: transformOkuGuidToBookGuid(entry.guid),
    PubDate: dbDate(entry.pubDate),
    Title: entry.title,
    Author: entry.creator,
    ImageUrl: entry.enclosure?.url,
    Description: entry.content,
    UpdateDate: dbDate(updateDate),
  };
}

function okuFeedToBookEvent(
  feedName: string,
  entry: OkuRawFeedEntry,
): OkuBookEventEntry {
  return {
    EventType: feedName,
    BookGuid: transformOkuGuidToBookGuid(entry.guid),
    EventDate: dbDate(entry.isoDate),
  };
}
