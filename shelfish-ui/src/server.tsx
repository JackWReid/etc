import Bun from "bun";
import { Elysia, t } from "elysia";
import { staticPlugin } from "@elysiajs/static";
import { html } from "@elysiajs/html";
import { renderToString } from "react-dom/server";
import { logger } from "@bogeychan/elysia-logger";

import { startService } from "./server/service";
import { getJobQueueCount, getJobList } from "./server/jobs";
import {
  getBooksByReadStatus,
  getBookById,
  getBooks,
  getBooksBySearch,
  markBook,
  getEventsByBookId,
} from "./server/db";

import BookTableBody from "./ui/components/BookBrowser/BookTableBody";
import { responseBadge } from "./ui/components/StatusBadges";
import { BooksPage } from "./ui/pages/Books";
import { BookSinglePage } from "./ui/pages/BookSingle";
import { JobsPage } from "./ui/pages/Jobs";
import { scrapeGoodreadsByIsbn } from "./server/scraping";

export async function start() {
  await startService();

  const app = new Elysia()
    .use(html())
    .use(logger())
    .use(staticPlugin({ prefix: "" }))
    .derive(async () => {
      const jobQueueCount = await getJobQueueCount();
      return { state: { jobQueueCount } };
    })
    .get("/", ({ redirect }) => {
      return redirect("/books");
    })
    .get("/books", async ({ state }) => {
      const books = await getBooks({});
      return renderToString(
        <BooksPage state={state} status="none" books={books} />,
      );
    })
    .get("/books/:status", async ({ state, params: { status } }) => {
      const books = await getBooksByReadStatus(status);
      return renderToString(
        <BooksPage state={state} status={status} books={books} />,
      );
    })
    .get("/book/:id", async ({ state, params: { id } }) => {
      const book = await getBookById(id);
      const bookEvents = await getEventsByBookId(id);
      return renderToString(
        <BookSinglePage state={state} book={book} bookEvents={bookEvents} />,
      );
    })
    .post(
      "/add",
      async ({ redirect, body }) => {
        if (body.isbn) {
          return redirect(`/add/${body.isbn}`);
        }
      },
      {
        body: t.Object({
          isbn: t.String(),
        }),
      },
    )
    .get(
      "/add/:isbn",
      async ({ state, params: { isbn } }) => {
        const grBook = await scrapeGoodreadsByIsbn({ isbn });
        return renderToString(<BookSinglePage book={grBook} />);
      },
      {
        params: t.Object({
          isbn: t.String(),
        }),
      },
    )
    .post(
      "/search",
      async ({ body }) => {
        const { bookSearch } = body;
        const books = await getBooksBySearch({ search: bookSearch });
        return renderToString(<BookTableBody books={books} />);
      },
      {
        body: t.Object({
          bookSearch: t.String(),
        }),
      },
    )
    .put(
      "/mark/:id",
      async ({ params, query }) => {
        let response = <span>Failed"</span>;

        const { id } = params;
        const { status_read, status_owned } = query;
        const book = await markBook(id, {
          status_read,
          status_owned,
        });

        response = responseBadge(book, { status_read, status_owned });
        return renderToString(response);
      },
      {
        params: t.Object({
          id: t.String(),
        }),
        query: t.Object({
          status_read: t.MaybeEmpty(t.String()),
          status_owned: t.MaybeEmpty(t.String()),
        }),
      },
    )
    .get("/jobs", async ({ state }) => {
      const jobs = await getJobList();
      return renderToString(<JobsPage state={state} jobs={jobs} />);
    })
    .listen(3000);
  console.log(`Listening on ${app.server!.url}`);
  return app;
}
