import { displayDate } from "../../../utils";
import BookFilter from "./BookFilter";
import BookTable from "./BookTable";

function BookCard({ book }) {
  return (
    <li key={book.id} className="book-timeline-item">
      <div className="book-timeline-item__media-card">
        <div className="book-timeline-item__cover">
          <img src={book.image_url} alt={`Cover of ${book.title}`} />
        </div>
        <div className="book-timeline-item__details">
          <p className="book-timeline-item__date">
            {displayDate(book.date_updated)}
          </p>
          <h2>
            <a href={`/book/${book.id}`}>{book.title}</a>
          </h2>
          <p>by {book.author}</p>
          {book.status_read === "read" && (
            <span className="bg-green-100 text-green-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-green-900 dark:text-green-300">
              Read
            </span>
          )}
          {book.status_read === "not-read" && (
            <span className="bg-red-100 text-red-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-red-900 dark:text-red-300">
              To Read
            </span>
          )}
          {book.status_read === "reading" && (
            <span className="bg-yellow-100 text-yellow-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-yellow-900 dark:text-yellow-300">
              Reading
            </span>
          )}
          <dl>
            <dt>ISBN</dt>
            <dd>{book.isbn}</dd>
            {book.oku_id && (
              <>
                <dt>Oku</dt>
                <dd>
                  <a href={`https://oku.club/book/${book.oku_id}`}>
                    {book.title}
                  </a>
                </dd>
              </>
            )}
            {book.amazon_id && (
              <>
                <dt>Amazon</dt>
                <dd>
                  <a href={`https://amazon.co.uk/dp/${book.amazon_id}`}>
                    {book.title}
                  </a>
                </dd>
              </>
            )}
          </dl>
        </div>
      </div>
    </li>
  );
}

export default function BookBrowser({ books }) {
  return (
    <div className="relative overflow-x-auto sm:rounded-lg">
      <BookFilter />
      <BookTable books={books} />
    </div>
  );
}
