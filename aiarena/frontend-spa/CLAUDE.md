# Frontend (SPA)

The Relay + React + Vite single-page app. (`aiarena/frontend/` is the older
Django-template frontend — different thing.)

## Verifying changes

Run `uv run dev pre-commit` from the repo root — it sequences the Relay
compiler, ESLint, and `tsc` correctly. Don't run `relay-compiler`, `eslint`, or
`tsc` directly. The Relay compiler also regenerates `__generated__/` types from
the GraphQL in your components, so run it after editing any `graphql` literal.

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

### Helpers (`@/_lib/relayHelpers`)

- **`getNodes(connection)`** — flatten a Relay connection's edges to a plain
  array (drops null nodes). Use it instead of hand-walking `edges`/`node`:
  ```tsx
  const newsData = getNodes(data.news);
  ```
- **`getIDFromBase64(globalId, "UserType")`** — decode a relay global ID back to
  the raw DB id, asserting the expected type. Used for building URLs that take a
  bare id.
