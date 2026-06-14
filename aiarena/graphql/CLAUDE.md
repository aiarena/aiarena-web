# GraphQL API (graphene)

The GraphQL schema, types, and mutations live here (graphene-django). The REST
arena-client API is separate (`aiarena/api/`).

## Authorizing objects referenced by ID — there is no automatic floor

### The mechanism

A mutation input typed as a `TypeModelChoice` ID (e.g. `BotID`, `MapID`)
resolves the global ID straight to a **live model instance** —
`model.objects.get(pk=...)` — *before* the mutation body runs, with **no
permission check**. So a caller can name any object by its global ID and the
mutation receives the real instance, whether or not the caller may see it.

There is **no automatic read floor** here. Authorization happens only when the
mutation *remembers* to check. This is the classic IDOR shape: forgetting a
check doesn't fail loudly — it silently lets a caller pull another user's
object into a structure they own and read it back.

### The rule: check every object you touch

A mutation that references a permissioned object must call:

```python
raise_for_access(info, instance, scopes=[...])
```

- The default scope is **write** (`SCOPE_WRITE`). Pass `scopes` explicitly when
  the intent differs (read-only reference, delete, etc.).
- The check routes through the central permission checker
  (`aiarena/core/permissions.py`) — `check.user(user, instance).can(scope)` — so
  access logic lives in one place, not scattered across mutations.
- Because the resolved instance arrives *before* the body, the check is the
  mutation's responsibility. Don't assume an object is safe just because it came
  in through a typed ID input — that resolution did no checking.

### When you add or edit a mutation

- For **every** object reached through an ID input, decide whether the caller
  may touch it, and `raise_for_access` for the right scope. The reference itself
  is not safe by default.
- Login is checked explicitly where required (mutations raise their own "you
  need to be logged in" error) — there's no global gate, so don't rely on one.

### Tests are the real backstop

Since nothing automatic stands behind these checks, the access-control tests are
the primary evidence the authorization is correct — not a nicety. For anything
permissioned, test all three callers: intended caller allowed, a different
regular user denied, anonymous denied. See `tests/CLAUDE.md`.
