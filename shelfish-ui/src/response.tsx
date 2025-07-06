import { type ReactElement } from "react";
import { renderToString } from "react-dom/server";

export function html(component: ReactElement, status = 200): Response {
  return new Response(renderToString(component), {
    status,
    headers: { "Content-Type": "text/html" },
  });
}
