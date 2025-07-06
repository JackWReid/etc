import Nav from "./Nav";
import Header from "./Header";

export function Layout({ state, title, children }) {
  return (
    <html>
      <head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta charSet="utf-8" />
        <link rel="stylesheet" href="/style.css" />
        <link
          href="https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist/flowbite.min.css"
          rel="stylesheet"
        />
        <script
          src="https://unpkg.com/htmx.org@2.0.1"
          integrity="sha384-QWGpdj554B4ETpJJC9z+ZHJcA/i59TyjxEPXiiUgN2WmTyV5OEZWCD6gQhgkdpB/"
          crossOrigin="anonymous"
        ></script>
      </head>
      <body>
        <Header />
        <Nav state={state} />
        <div className="p-4 mt-16 sm:ml-64">{children}</div>
        <script src="https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist/flowbite.min.js"></script>
      </body>
    </html>
  );
}
