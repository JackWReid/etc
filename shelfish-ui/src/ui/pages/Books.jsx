import { titleCase } from "../../utils";

import { Layout } from "../components/Layout";
import BookBrowser from "../components/BookBrowser";

export function BooksPage({ state, status, books }) {
  const title = titleCase(status);

  return (
    <Layout state={state} title={title}>
      <div>
        <BookBrowser books={books} />
      </div>
    </Layout>
  );
}
