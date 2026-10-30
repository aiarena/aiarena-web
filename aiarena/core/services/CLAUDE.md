# Core services

## Download rate limiting

Downloads of large assets (bot archives, replays, logs, maps) are direct AWS S3
egress cost. To bound that cost, download volume is metered per user — and, in the
final design, per membership tier — against an hourly and a monthly ceiling.

### The boundary: meter where a direct-to-S3 download is handed out

The end state is that every asset is fetched straight from S3 via a presigned URL,
so we never see the bytes. The moment we *hand out* such a URL is therefore the
moment we must count it. Every site that issues a presigned S3 URL (or otherwise
returns an asset's S3 URL) routes through the one metering entry point.

Serving an asset *through the app* instead of from S3 is a legacy path. Those sites
are the exception: they are metered at serve time and are expected to migrate to
presigned-URL issuance, after which the app-proxied download can be removed.

Uploads of user assets count against the uploader's download budget: publishing a
new bot archive forces every arena client to re-download it, so the cost is the
uploader's.

### A row is an egress event, not an attempt

The unit of accounting is **one row per download that moves bytes** (i.e. one that
is within limits). The limit decision is a `SUM` of those rows' sizes over the
current window. Two consequences follow, and they are the heart of the design:

- **Denials are counters, never rows.** A rejected request transfers nothing — it
  is not an egress event — so it does not get a row. Instead it increments a small
  per-(user, hour) tally. This is deliberate: a misbehaving client or crawler can
  hammer a rejected endpoint without bound, and if each attempt were a row it would
  bloat the table and the indexes it must carry. Collapsing a flood of rejections
  into increments on one counter row keeps the table proportional to *real traffic*,
  not to *attempts*. The tally still records the would-be (observe mode) or avoided
  (enforcement) byte volume, so overrun stays measurable.
- **Enforcement bounds the table.** Once limits are enforced, granted egress is
  capped by the limits themselves, so the row count is self-limiting. The unbounded
  dimension — rejections — lives entirely in the counters.

This also decouples the schema from the Django version: there is no unique index on
a nullable column anywhere here, so nothing in this feature gates on (or is gated
by) a Django upgrade.

### Windows are calendar, not rolling

The hourly and monthly windows are **calendar** windows (start of the current UTC
hour / month), compared by a timestamp range on the rows. This is a deliberate
choice over rolling (trailing-duration) windows:

- A scalar counter can only represent a calendar window — a rolling window would
  require per-event rows to let old entries age out, which is exactly the unbounded
  table we avoid for denials.
- The monthly window aligns with the AWS billing month, so "stayed under quota" maps
  onto "stayed under the bill", and it matches the monthly Patreon membership model.

The known cost is the **boundary double-burst**: a user can spend a full window's
allowance just before a boundary and again just after. For a *cost safeguard* (not a
security control) that bounded leak is acceptable, and it is the price of counter
compatibility and billing alignment.

### Invariants

- **Fail open.** Metering must never break a download. If the accounting itself
  errors, the download is allowed and the error is logged.
- **Never cache file sizes.** An asset's size (and etag) is read live from S3 when
  needed. Storing it locally invites drift from S3 and is deliberately avoided.
- **One bucket for anonymous traffic.** All unauthenticated requests share a single
  bucket — rows and counters keyed on a NULL user; each authenticated user has their
  own.

### Concurrency: no locks on the critical path

The grant path is lock-free by construction: the decision is a read (`SUM`) and the
record is an append (`INSERT`). There is no shared row to serialize on, so a rare
concurrent overshoot of a few KB is possible and accepted — cheaper than a lock, and
immaterial for a cost safeguard.

The one piece of shared mutable state is the denial counter. It is incremented with
a single atomic `UPDATE` (no `select_for_update`, no read-modify-write in Python),
and — crucially — it gates nothing: the link is already issued by the time we touch
it, so even under a flood it can only slow the counter writes, never a download.

A single hot counter row (the shared anonymous bucket under a crawler flood) still
serializes at the database's row lock for the duration of each `UPDATE`. That is
intrinsic to keeping one running total and is harmless here because the write is off
the critical path and best-effort. **If that row ever becomes a throughput
hotspot**, the standard escape hatch is to *shard the counter* — keep N rows per
(user, window), increment one at random, and `SUM` them on read — trading a little
read complexity for N-way less write contention. Not worth building until measured.

### Retention

Accounting rows are pruned daily to the last few calendar months
(`DOWNLOAD_RECORD_RETENTION_MONTHS`). The limit itself only ever needs the current
month; the extra history exists for insight and for reconciling against the AWS
bill, so the retention horizon is a policy choice, not a correctness requirement.
Postgres has no native row TTL, so the prune is a scheduled delete run from a Celery
beat task.

### Rollout is staged

The first step runs the metering in *observe mode*: it records what each request
would consume and whether it would be allowed, but always issues the link, under one
flat limit for all tiers. This gathers real usage before any enforcement or per-tier
limits are turned on. The entry point already returns the allow/deny decision —
callers simply don't act on it yet. Later steps enforce it and split the limits by
tier.
