import {
  URL_DEFINITIONS,
  UrlName,
  UrlParams,
} from "@/__generated__/urlDefinitions";

/**
 * Build a URL by Django URL name, the frontend counterpart to Django's `reverse`.
 *
 * The name and its parameters are type-checked against the routes generated from
 * `urls.py` (see `__generated__/urlDefinitions.ts`), so a renamed or removed route
 * is a compile error, not a broken link at runtime.
 *
 *   reverseUrl("home")                       // "/"
 *   reverseUrl("bot", { pk: 42 })            // "/bots/42/"
 *   reverseUrl("author", { pk: rawUserId })  // "/authors/7/"
 *
 * Pass the raw database id (e.g. via `getIDFromBase64`), not a Relay global id.
 */
export function reverseUrl<T extends UrlName>(
  ...args: UrlParams[T] extends Record<string, never>
    ? [name: T]
    : [name: T, params: UrlParams[T]]
): string {
  const [name, params] = args;
  let url: string = URL_DEFINITIONS[name];
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`<${key}>`, String(value));
    }
  }
  return url;
}
