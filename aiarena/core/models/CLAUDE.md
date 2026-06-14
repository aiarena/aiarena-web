# Models

## Zero-downtime migrations

### The invariant everything follows from

Our deploy runs migrations **first, once, from CI** (`deploy migrate-and-update`
→ `manage.py migrate`, then the ECS services roll over to the new image). So
there is always a window where the **old** application code is running against
the **already-migrated** schema, and during the rolling update old and new code
run **simultaneously**.

That gives one rule the rest of this file is just instances of:

> **Every migration must leave the schema compatible with the *currently
> deployed* (old) code.** A schema change and the code that depends on it cannot
> ship in the same deploy if the change would break the old code mid-rollout.

When a change can't satisfy that in one step, split it across **two deploys**,
each of which is individually safe. "Broken only for a few seconds
during rollout" is still downtime — design it out, don't tolerate it.

(Migrations run as a root DB user on purpose, so long-running ones aren't killed
mid-statement. Don't move migrations into app startup — that reintroduces the
parallel-execution and partial-failure problems this ordering exists to avoid.)

### Adding a column

Old code still runs `INSERT`s that don't mention the new column, so a
non-nullable column with no usable default makes those inserts fail.

**Deploy 1 — add as nullable, with a marker:**
```python
# TODO(make-not-null): Remove null=True in a follow-up migration after deploy
new_field = models.BooleanField(null=True, default=False)
```
New code can read/write it; old code inserting NULL is fine.

**Deploy 2 — backfill existing rows, then drop `null=True`:**
```python
new_field = models.BooleanField(default=False)
```
By now every running instance writes the field, so backfilling and enforcing
NOT NULL is safe.

Find the fields still waiting on their step 2:
```bash
grep -rn "TODO(make-not-null)" aiarena/core/models/
```

> Don't lean on a DB-level `default` to skip the split — adding a volatile/heavy
> default can itself be a locking operation, and it doesn't make the old↔new code
> contract safe. The two-deploy split is the real fix.

### Removing a column

The mirror image — drop the **code** before the **column**.

- **Deploy 1:** remove every reference to the column in code; if it's currently
  NOT NULL, also make it nullable (so old code's inserts, which still set it,
  and new code's inserts, which don't, both succeed during rollout).
- **Deploy 2:** drop the column once no running code touches it.

Dropping a column while old code still selects/writes it is an immediate error
for that old code — that's the window to avoid.

### Renaming a column or changing its type

A rename is a drop + add in disguise — never a single `RenameField` in one
deploy, because old code reads the old name while new code reads the new one.
Expand-then-contract across deploys:

1. **Add** the new column (nullable). Have the code write **both** old and new.
2. **Backfill** the new column, switch reads to it, make it NOT NULL.
3. **Stop writing** the old column; make it nullable.
4. **Drop** the old column.

Same shape for a type change: add a new column of the new type, dual-write,
backfill+convert, cut over, drop the old.

### Indexes — build them CONCURRENTLY (Postgres)

A plain `CREATE INDEX` takes a lock that blocks writes on the table for the
duration — on a large table that's an outage. On Postgres, build indexes
concurrently so writes keep flowing. In Django use
`AddIndexConcurrently` / `RemoveIndexConcurrently` from
`django.contrib.postgres.operations`, and mark the migration
`atomic = False` (concurrent index builds can't run inside a transaction).

### Data migrations

Backfills run in the same migrate-first window, so: only transform data that the
**old** code isn't actively reading or writing in a conflicting way, and for big
tables do it in **batches** rather than one statement that locks the table or
runs for many minutes. A backfill belongs *between* the expand and contract
steps above — never in the same step that flips a column to NOT NULL.
