import { describe, test, expect } from "bun:test";
import { getBooksBySearch, addNewBook } from "../server/db";
import { scrapeGoodreadsByIsbn } from "../server/scraping";

describe("getBooksBySearch", () => {
  test("returns based on title Like Love", async () => {
    const results = await getBooksBySearch({ search: "Like Love" });
    expect(results.length).toBeGreaterThan(0);
    const firstResult = results[0];
    expect(firstResult.title).toEqual("Like Love");
    expect(firstResult.isbn).toEqual("1644452812");
  });

  test("returns nothing for gibberish", async () => {
    const results = await getBooksBySearch({ search: "sfjlhsfjhf3f" });
    expect(results.length).toEqual(0);
  });

  test("returns nothing for empty query", async () => {
    const results = await getBooksBySearch({ search: "" });
    expect(results.length).toEqual(0);
  });

  test("returns nothing for malformed query", async () => {
    const results = await getBooksBySearch({ q: "f" });
    expect(results.length).toEqual(0);
  });
});

describe("scrapeGoodreadsByIsbn", () => {
  test("scrapes good", async () => {
    const isbn = "9781250777355";
    const grBook = await scrapeGoodreadsByIsbn({ isbn });
    expect(grBook.title).toEqual(
      "Emotional Labor: The Invisible Work Shaping Our Lives and How to Claim Our Power",
    );
  });
});

describe("addNewBook", () => {
  test("adds a new book", async () => {
    const isbn = "9781473695702";
    const grBook = await scrapeGoodreadsByIsbn({ isbn });
    const result = await addNewBook("not-read", "not-owned", grBook);
    expect(result.title).toEqual("The Ottomans: Khans, Caesars and Caliphs");
    expect(result.status_owned).toEqual("not-owned");
    expect(result.status_read).toEqual("not-read");
    // expect(result.goodreads_id).toEqual("56269593-the-ottomans");
    // expect(result.author).toEqual("Marc David Baer");
  });

  // test("rejects bad read status", async () => {
  //   const isbn = "9781473695702";
  //   const grBook = await scrapeGoodreadsByIsbn({ isbn });
  //   const result = await addNewBook("bad-read", "not-owned", grBook);
  //   expect(result).toBe(null);
  //   expect(result.title).toEqual("The Ottomans: Khans, Caesars and Caliphs");
  //   expect(result.status_owned).toEqual("not-owned");
  //   expect(result.status_read).toEqual("not-read");
  //   expect(result.goodreads_id).toEqual("56269593-the-ottomans");
  //   expect(result.author).toEqual("Marc David Baer");
  // });

  // test("rejects bad read status", async () => {
  //   const isbn = "9781473695702";
  //   const grBook = await scrapeGoodreadsByIsbn({ isbn });
  //   const result = await addNewBook("not-read", "bad-owned", grBook);
  //   expect(result).toBe(null);
  //   expect(result.title).toEqual("The Ottomans: Khans, Caesars and Caliphs");
  //   expect(result.status_owned).toEqual("not-owned");
  //   expect(result.status_read).toEqual("not-read");
  //   expect(result.goodreads_id).toEqual("56269593-the-ottomans");
  //   expect(result.author).toEqual("Marc David Baer");
  // });
});
