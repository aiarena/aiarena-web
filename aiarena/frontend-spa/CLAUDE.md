# Frontend (SPA)

The Relay + React + Vite single-page app. (`aiarena/frontend/` is the older
Django-template frontend — different thing.)

## Verifying changes

Run `uv run dev pre-commit` from the repo root — it sequences the Relay
compiler, ESLint, and `tsc` correctly. Don't run `relay-compiler`, `eslint`, or
`tsc` directly. The Relay compiler also regenerates `__generated__/` types from
the GraphQL in your components, so run it after editing any `graphql` literal.

The same command regenerates `src/__generated__/urlDefinitions.ts` from Django's
`urls.py` (see "Linking to URLs" below), so run it after adding or renaming a
route too.

## GraphQL & Relay patterns

### Core principles

1. **Fragments define data requirements** — a component declares the data it
   needs via a GraphQL fragment, not by reaching into a parent's data.
2. **Use generated types only** — never hand-write TypeScript types for GraphQL
   data; import them from the component's `./__generated__/` files.
3. **Fragment naming is `ComponentName_propName`** (e.g. `AvatarWithBorder_user`,
   `UserBotsList_user`). The Relay compiler enforces this, so component names
   must be unique across the app.

### Fragment keys come in as props, resolved with `useFragment`

A child component takes a fragment **key** as a prop and resolves it. The prop is
named after the data, and its type is `ComponentName_propName$key`:

```tsx
export interface AvatarWithBorderProps {
  size?: "sm" | "lg" | "xl";
  user: AvatarWithBorder_user$key;
}

export default function AvatarWithBorder(props: AvatarWithBorderProps) {
  const user = useFragment(
    graphql`
      fragment AvatarWithBorder_user on UserType {
        patreonLevel
        avatarUrl
      }
    `,
    props.user,
  );
  // `user` is the resolved data; `props.user` was the key
}
```

Nested objects that carry a child fragment spread become fragment keys for that
child — pass them straight down: `<ChildCard thing={parent.thing} />`.

### Inline the `graphql` literal

Always inline the `graphql` tagged template directly in `useFragment`,
`useLazyLoadQuery`, and `useMutation`. Don't extract it to a variable — keeping it
at the call site is what lets the compiler associate it and generate types.

### Two data-loading patterns

- **Fragment (data from parent)** — the common case for cards/items in a list.
  The component declares a fragment; the parent supplies the key.
- **Query (independent load)** — a component that fetches its own data with
  `useLazyLoadQuery<ComponentQuery>(...)`. Use for page sections / tab content
  that should load independently with their own loading state.

### Always define your own fragment, even a passthrough

A component that consumes GraphQL data should declare its **own** fragment and
resolve it with `useFragment`, even when all it does is spread a child's
fragment:

```tsx
fragment UserBotsSection_viewer on Viewer {
  activeBotParticipations
  user {
    ...UserBotsList_user   // spread the child here
  }
}
```

This keeps the file self-contained (its data needs live next to its code), gives
it a natural home for fields it'll need later, and means adding a second child
only touches this fragment — not every call site that renders the component.

A component with a query does the same: define its own fragment and spread it
into the query (`JoinCompetitionModal` is an example — it holds a `useFragment`,
a `useLazyLoadQuery`, and a `useMutation` together). Routing the query's data
through a fragment is also what lets a mutation refetch exactly that component's
data.

### Page shells stay lightweight; sections load independently

For a page with sections or tabs, keep the top-level query thin and let each
section fetch its own data under `Suspense`, with a skeleton fallback. The
`*Page` → `*Section` split throughout `_pages/` is this pattern: the shell
renders immediately, each section suspends on its own data, and Relay's store
caches it so revisiting a section doesn't refetch.

### Mutations

Every mutation exposes three fields on its result, regardless of what it does:
`errors`, `node(id:)`, and `viewer`. Lean on them instead of expecting a bespoke
return field.

**Always select `errors` and handle them.** Drive the mutation through
`useBackendErrors` (or `useSnackbarErrorHandlers`, which wraps it) — these read
`response[mutationName].errors` and surface form/validation messages. Selecting
`errors` is the convention; omitting it means errors pass silently.

**Read results back through `node`/`viewer`, not bespoke fields.** To see the
effect of a mutation:

- For an object you already have the ID of (the usual *update* case — you passed
  the ID in), select it back via `node`. Pass the id as a variable and spread the
  fragment you need:
  ```tsx
  mutation BotSettingsModalMutation($input: UpdateBotInput!, $botId: ID!) {
    updateBot(input: $input) {
      node(id: $botId) {
        ... on BotType { ...BotSettings_bot }
      }
      errors { field messages }
    }
  }
  ```
  Relay merges the returned object into its store by ID, so the UI updates.
- For changed current-user state (counts, flags), select `viewer { ... }`.
- Only a **newly-created** object whose ID you couldn't know in advance comes
  back on a dedicated field (e.g. `requestMatch { match { ... } }`,
  `uploadBot { bot { ... } }`).

## Linking to URLs

### `urls.py` is the source of truth for navigation

Every place the app can navigate to is a **named route in Django's `urls.py`** —
including the routes that only render in React (they point at the SPA-serving
view). This is deliberate, for two reasons:

- **No dead links.** Routes flow from one declaration into typed frontend
  helpers, so a renamed or deleted route becomes a compile error, not a 404
  discovered in production.
- **Hard-refresh works.** If a path the SPA renders isn't declared server-side,
  loading it directly (refresh, pasted link, email) hits Django, finds nothing,
  and 404s instead of letting React render. So when you add an SPA route in
  `App.tsx`, add a matching named route in `urls.py` too.

When `urls.py` can't yet express something the frontend needs (an unnamed route,
a page that only existed client-side), the fix is to **change `urls.py`** — add
the `name=`, declare the route — not to hand-build a path around it.

### Build URLs with `reverseUrl`, never by hand

`reverseUrl` (`@/_lib/reverseUrl`) is the frontend counterpart to Django's
`reverse`. Never hand-write a path like `` `/bots/${id}` ``.

```tsx
import { reverseUrl } from "@/_lib/reverseUrl";

reverseUrl("home");                                    // "/"
reverseUrl("bot", { pk: getIDFromBase64(bot.id, "BotType") });  // "/bots/42/"
```

Route names and their params are generated from `urls.py` into
`__generated__/urlDefinitions.ts` (regenerated by `uv run dev pre-commit`), so
names autocomplete and params are type-checked. The generated path *is* Django's
`reverse()` output — a Playwright test asserts `reverseUrl` and `reverse` agree
for every route — so the two are guaranteed interchangeable, and a link built
here resolves identically whether the SPA navigates to it or the server does.

`pk` and other params are **non-nullable** by design. Routes take a raw database
id, which you get from `getIDFromBase64` — and that returns `string | null` when
the source field is nullable. Let the type checker force you to resolve the null
*before* calling `reverseUrl`: guard and render a non-link (or nothing) when the
id is genuinely absent. Don't assert it away with `!` — that just recreates the
`/bots/null` links this is meant to prevent.

### `reverseUrl` for cross-page links; relative nav for in-page tabs

`reverseUrl` builds **absolute** paths — use it for navigating *to a different
page*. For switching tabs or sections *within an already-mounted nested-route
shell* (the competition-stats tabs, the dashboard sub-nav), use react-router's
**relative** navigation (a bare segment like `"maps"` / `"elograph"`). Those
moves swap an `<Outlet>` inside the current page; relative nav is the idiomatic
tool and avoids threading the parent route's id through every tab button. The
tabs are still named routes in `urls.py` (so they're hard-refreshable and
reversible from the server) — they just aren't navigated to via `reverseUrl`
from inside their own shell.

## Helpers (`@/_lib/relayHelpers`)

- **`getNodes(connection)`** — flatten a Relay connection's edges to a plain
  array (drops null nodes). Use it instead of hand-walking `edges`/`node`:
  ```tsx
  const newsData = getNodes(data.news);
  ```
- **`getIDFromBase64(globalId, "UserType")`** — decode a Relay global ID to the
  raw DB id (what `reverseUrl` params want). The return type mirrors the input:
  a non-null id in gives `string` out, a nullable id gives `string | null`, so
  the absent-id case surfaces to you. A type *mismatch* or malformed id throws —
  those mean the wrong field or type literal was wired up, which is a bug, not a
  runtime condition.
