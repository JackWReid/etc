import * as cheerio from "cheerio";
import { bookToSeachParams, dbDate } from "../utils";
import type { GoodreadsScrapeBook } from "./types";

export async function scrapeGoodreadsByIsbn(
  payload,
): Promise<GoodreadsScrapeBook> {
  const searchUrl = `https://www.goodreads.com/search?q=${payload.isbn}`;
  return await goodreadsUrlToBook(searchUrl);
}

export async function scrapeGoodreadsByTitleAuthor(
  payload,
): Promise<GoodreadsScrapeBook> {
  const searchUrl = `https://www.goodreads.com/search${bookToSeachParams(payload)}`;
  const searchResponse = await fetch(searchUrl);
  const searchText = await searchResponse.text();
  const search$ = cheerio.load(searchText);

  const bookPathname = search$(`[itemtype=http://schema.org/Book]`)
    .first()
    .find(".bookTitle")
    .attr("href");

  const bookUrl = new URL(bookPathname, "https://www.goodreads.com").toString();
  return await goodreadsUrlToBook(bookUrl);
}

export async function goodreadsUrlToBook(
  bookUrl: string,
): Promise<GoodreadsScrapeBook> {
  const bookResponse = await fetch(bookUrl);
  const bookText = await bookResponse.text();
  const book$ = cheerio.load(bookText);
  const bookPageData = JSON.parse(book$("#__NEXT_DATA__").text()).props
    .pageProps;

  const apolloBookQuery = Object.values(bookPageData.apolloState).find(
    (o) => o["__typename"] === "Book",
  );

  const bookData = {
    id: bookPageData.params.book_id,
    title: apolloBookQuery.titleComplete,
    description: apolloBookQuery.description,
    image: apolloBookQuery.imageUrl,
    isbn: apolloBookQuery.details.isbn,
    isbn13: apolloBookQuery.details.isbn13,
    asin: apolloBookQuery.details.asin,
    datePublished: dbDate(apolloBookQuery.details.publicationTime),
    publisher: apolloBookQuery.details.publisher,
    genres: apolloBookQuery.bookGenres.map((g) => g.genre.name.toLowerCase()),
    amazonId:
      apolloBookQuery["links({})"].secondaryAffiliateLinks[0].url.split("/")[5],
  };

  return bookData;
}
