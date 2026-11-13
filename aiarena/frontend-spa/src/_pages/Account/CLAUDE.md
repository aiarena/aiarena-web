# Account pages

Login, registration + activation, password reset and password change. Each page
is a thin form over one account GraphQL mutation; validation lives in the
backend (the same Django forms the old template views used), so the frontend
only renders the errors it gets back — don't re-implement password rules here.

## Things that look optional but aren't

- **Signing in ends with a full page navigation, not client-side routing.**
  Django rotates the CSRF token on login, and the SPA reads its token once at
  page load — a client-side route change would leave every later mutation
  failing CSRF. The `next` target may also be a server-rendered page.

- **The backend decides where to go after signing in, not the page.** The page
  passes `?next=` through untouched and navigates to whatever redirect the
  sign-in mutation returns. Whether `next` is a safe same-site URL is checked
  server-side with Django's own open-redirect guard; hand-rolled checks in the
  browser ("starts with `/` but not `//`") were bypassable with backslashes and
  control characters. Don't reintroduce a frontend check or a frontend default.

- **The route paths and names are referenced by emails already in inboxes.**
  Activation and password-reset emails are rendered server-side by reversing
  these route names, and old emails keep pointing at the old paths. Renaming or
  moving one of them silently breaks every unclicked link. Treat them as fixed.

- **"Resend activation" and "Forgot password" always say the same thing.**
  The success message is identical whether or not the address has an account,
  so the forms can't be used to discover who is registered. Keep it that way
  when touching the copy.

- **An activation key works once.** The activation page fires its mutation on
  arrival and must fire it exactly once — React StrictMode mounts twice in
  development, and a second call would turn a successful activation into an
  "invalid link" error.

## Errors

Backend errors for a field the form shows go under that input; everything else
(`__all__`, a bad `token` / `activationKey`, network failures) is shown at the
top of the card. An invalid reset/activation link can't be fixed by retyping, so
those pages swap the form for a link to request a new one.
