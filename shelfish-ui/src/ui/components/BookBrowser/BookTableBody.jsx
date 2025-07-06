import { displayDate, randomCoverPlaceHolder } from "../../../utils";
import StatusBadges from "../StatusBadges";

export default function BookTableBody({ books }) {
  return (
    <>
      {books.map((book) => (
        <tr
          key={book.id}
          className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
        >
          <td className="p-4">
            <img
              loading="lazy"
              src={book.image_url || randomCoverPlaceHolder()}
              className="w-16 md:w-32 max-w-full max-h-full"
              alt={`Cover of ${book.title}`}
            />
          </td>
          <td className="px-6 py-4">
            <span className="block text-sm text-gray-500 dark:text-gray-400">
              {displayDate(book.date_last_read_event)}
            </span>
            <span className="inline-block max-w-md text-2xl font-semibold">
              <a className="text-gray-800" href={`/book/${book.id}`}>
                {book.title}
              </a>
            </span>
            <span className="block text-sm">by {book.author}</span>
          </td>
          <td className="px-6 py-4">
            <StatusBadges book={book} />
          </td>
          <td className="px-6 py-4">
            {book.isbn && (
              <span className="bg-gray-100 text-gray-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-gray-400 border border-gray-500">
                {book.isbn}
              </span>
            )}
            {book.oku_id && (
              <a
                href={`https://oku.club/book/${book.oku_id}`}
                className="inline-block bg-gray-100 text-gray-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-gray-400 border border-gray-500"
              >
                Oku
              </a>
            )}
            {book.goodreads_id && (
              <a
                href={`https://www.goodreads.com/books/show/${book.goodreads_id}`}
                className="inline-block bg-yellow-100 text-yellow-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-yellow-300 border border-yellow-300"
              >
                Goodreads
              </a>
            )}
            {book.amazon_id && (
              <a
                href={`https://amazon.co.uk/dp/${book.amazon_id}`}
                className="inline-block bg-yellow-100 text-yellow-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-yellow-300 border border-yellow-300"
              >
                Amazon
              </a>
            )}
          </td>
        </tr>
      ))}
    </>
  );
}
