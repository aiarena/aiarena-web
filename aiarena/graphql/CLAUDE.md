# GraphQL API (graphene)

The GraphQL schema, types, and mutations live here (graphene-django). The REST
arena-client API is separate (`aiarena/api/`).

## Login is required by default

Every mutation inherits from `BaseMutation`, which enforces authentication
**before** the mutation body runs. You don't write a login check — it's the
default. A mutation opts out only by setting `allow_anonymous = True` in its
`Meta`, which should be reserved for actions that are *unauthenticated by
definition*: signing in is the only legitimate case (you can't be logged in
while logging in). Everything else — including sign-out and token regeneration —
is a normal authenticated mutation.

Resist the pull to mark a mutation `allow_anonymous` and then re-check auth by
hand in the body (e.g. returning a "you're not signed in" payload). That opts
out of the secure default only to reimplement it worse. Denying a logged-out
caller at the gate is the honest behavior: a frontend with stale auth state
learns its session is gone, instead of getting a no-op that reports success.

`PasswordSignIn` should be the only `allow_anonymous` mutation in the schema. If
you're adding a second, that's a strong signal to stop and reconsider.

## Authorizing the objects a mutation touches

### The mechanism, and why it needs care

A mutation input typed as a `TypeModelChoice` ID (e.g. `BotID`, `MatchID`,
`TemporaryUploadID`) resolves the global ID straight to a **live model
instance** — `model.objects.get(pk=...)` — before the body runs, with **no
permission check**. So a caller can name any object by its global ID and the
mutation receives the real instance. This is the classic IDOR shape: a mutation
that writes through, or copies from, a referenced object without checking
ownership lets a caller act on objects that aren't theirs.

Objects are world-readable by design — the permission default in
`core/permissions.py` grants READ to everyone — so referencing an object by ID is
not itself a leak. The boundaries that matter are **write/delete on objects** and
**field-level reads**; that's where checks go.

### Write/delete: check explicitly in the body

When a mutation *mutates* (or deletes) a referenced object, check it:

```python
raise_for_access(info, instance, scopes=[...])  # default scope is SCOPE_WRITE
```

It routes through the central checker (`core/permissions.py`) so access logic
lives in one place. Only the mutation knows which of its inputs it actually
writes vs. merely reads, so this stays explicit — see `UpdateBot` /
`UpdateCompetitionParticipation` gating on the bot's owner.

### Cross-account references: check ownership even when you don't mutate

If a mutation *consumes* a referenced object's contents without writing the
object itself, it still needs an ownership check. See `SubmitResult`: it copies
the contents of `TemporaryUpload`s named by ID into the result, and each upload's
`clean_*` guard verifies `uploaded_by == caller`. Without that, one arena client
could reference another's upload by ID (sequential PK, guessable) and graft its
contents into their submission.

### Field-level reads are the real read-side boundary

Objects are public, but specific *fields* are not — e.g. a bot's zip is
downloadable only if the owner made it public. That gate lives on the **type's
field resolver**, not on any mutation: `BotType.resolve_bot_zip_url` returns the
signed URL only when `can_download_bot_zip(viewer)` passes (and the download view
`can_access_file` enforces the same at serve time). When you add a field that
exposes something not everyone may see, gate it in its resolver — that is where
read authorization happens in this schema.

## Denial messages are unified

All access denials share one prefix so tests assert a constant, not brittle
wording (a copy change is then one edit):

- `NO_ACCESS_MESSAGE_PREFIX` — every object-access denial (`raise_for_access`
  builds on it via `no_access_message`, which appends an optional
  `(tried to {scope})` hint). Verb-neutral on purpose.
- `NOT_LOGGED_IN_MESSAGE` — the login-by-default denial; separate because it
  isn't about a specific object.

Assert against these constants in tests, never the literal string.

## Tests are the real backstop

Access control here is enforced by hand-written checks, so the tests are the
primary evidence it's correct — not a nicety. For anything permissioned, test
all three callers explicitly: the intended caller is allowed, a different regular
user is denied, and an anonymous caller is denied. See `tests/CLAUDE.md`.
