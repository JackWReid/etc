export function StatusBadgeRead({ book }) {
  return (
    <span
      hx-put={`/mark/${book.id}?status_read=read`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-green-100 text-green-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-green-900 dark:text-green-300"
    >
      Read
    </span>
  );
}

export function StatusBadgeToRead({ book }) {
  return (
    <span
      hx-put={`/mark/${book.id}?status_read=not-read`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-red-100 text-red-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-red-900 dark:text-red-300"
    >
      To Read
    </span>
  );
}

export function StatusBadgeReading({ book }) {
  return (
    <span
      hx-put={`/mark/${book.id}?status_read=reading`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-yellow-100 text-yellow-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-yellow-900 dark:text-yellow-300"
    >
      Reading
    </span>
  );
}

export function StatusBadgeOwned({ book }) {
  return (
    <span
      hx-put={`/mark/${book.id}?status_owned=on-loan`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-green-100 text-green-800 text-sm font-medium me-2 px-2 py-0 rounded dark:bg-gray-700 dark:text-green-400 border border-green-400"
    >
      Owned
    </span>
  );
}

export function StatusBadgeOnLoan({ book }) {
  return (
    <span
      hx-put={`/mark/${book.id}?status_owned=wanted`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-yellow-100 text-yellow-800 text-sm font-medium me-2 px-2 py-0 rounded dark:bg-gray-700 dark:text-yellow-400 border border-yellow-400"
    >
      On Loan
    </span>
  );
}

export function StatusBadgeNotOwned({ book }) {
  return (
    <button
      hx-put={`/mark/${book.id}?status_owned=owned`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-red-100 text-red-800 text-sm font-medium me-2 px-2 py-0 rounded dark:bg-gray-700 dark:text-red-400 border border-red-400"
    >
      Not Owned
    </button>
  );
}

export function StatusBadgeWanted({ book }) {
  return (
    <span
      hx-put={`/mark/${book.id}?status_owned=owned`}
      hx-trigger="click"
      hx-swap="outerHTML"
      className="inline-block bg-purple-100 text-purple-800 text-sm font-medium me-2 px-2 py-0 rounded dark:bg-gray-700 dark:text-purple-400 border border-purple-400"
    >
      Wanted
    </span>
  );
}

export function responseBadge(book, { status_read, status_owned }) {
  if (status_read === "read") {
    return <StatusBadgeRead book={book} />;
  }

  if (status_read === "not-read") {
    return <StatusBadgeToRead book={book} />;
  }

  if (status_read === "reading") {
    return <StatusBadgeReading book={book} />;
  }

  if (status_owned === "owned") {
    return <StatusBadgeOwned book={book} />;
  }

  if (status_owned === "on-loan") {
    return <StatusBadgeOnLoan book={book} />;
  }

  if (status_owned === "not-owned") {
    return <StatusBadgeNotOwned book={book} />;
  }

  if (status_owned === "wanted") {
    return <StatusBadgeWanted book={book} />;
  }

  return null;
}

export default function StatusBadgeSet({ book }) {
  return (
    <>
      {book.status_read === "read" && <StatusBadgeRead book={book} />}
      {book.status_read === "not-read" && <StatusBadgeToRead book={book} />}
      {book.status_read === "reading" && <StatusBadgeReading book={book} />}
      {book.status_owned === "owned" && <StatusBadgeOwned book={book} />}
      {book.status_owned === "on-loan" && <StatusBadgeOnLoan book={book} />}
      {book.status_owned === "not-owned" && <StatusBadgeNotOwned book={book} />}
      {book.status_owned === "wanted" && <StatusBadgeWanted book={book} />}
    </>
  );
}
