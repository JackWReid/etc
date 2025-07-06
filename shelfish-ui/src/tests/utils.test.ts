import { describe, test, expect } from "bun:test";
import { dbDate, displayDate, olderThanHours } from "../utils";

describe("dbDate", () => {
  test("converts UNIX time to DB date standard", () => {
    expect(dbDate(0)).toBe("1970-01-01 00:00:00");
    expect(dbDate(new Date(0))).toBe("1970-01-01 00:00:00");
  });

  test("converts SQLite format to DB date standard", () => {
    expect(dbDate("19/03/2016 02:14:25")).toBe("2016-03-19 02:14:25");
  });

  test("converts ISO format to DB date standard", () => {
    expect(dbDate("Fri, 19 Jul 2024 13:39:56 +0000")).toBe(
      "2024-07-19 13:39:56",
    );
    expect(dbDate(new Date("Fri, 19 Jul 2024 13:39:56 +0000"))).toBe(
      "2024-07-19 13:39:56",
    );
  });
});

describe("displayDate", () => {
  test("Display output", () => {
    const dbDateStr = dbDate("19/03/2016 02:14:25");
    const displayDateStr = displayDate(dbDateStr);
    expect(displayDateStr).toBe("19th Mar '16, 02:14");
  });
});

describe("olderThanHours", () => {
  test("Fresh dates not older", () => {
    expect(olderThanHours(1, new Date())).toBe(false);
    expect(olderThanHours(24, new Date())).toBe(false);
    expect(olderThanHours(24, dbDate(new Date()))).toBe(false);
  });

  test("Stale dates older", () => {
    const twoDaysAgo = new Date(new Date().getTime() - 2 * 24 * 60 * 60 * 1000);
    expect(olderThanHours(1, twoDaysAgo)).toBe(true);
    expect(olderThanHours(24, twoDaysAgo)).toBe(true);
    expect(olderThanHours(24, dbDate(twoDaysAgo))).toBe(true);
  });
});
