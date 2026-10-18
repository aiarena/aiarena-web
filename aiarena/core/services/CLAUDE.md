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

### Invariants

- **Fail open.** Metering must never break a download. If the accounting itself
  errors, the download is allowed and the error is logged.
- **Never cache file sizes.** An asset's size (and etag) is read live from S3 when
  needed. Storing it locally invites drift from S3 and is deliberately avoided.
- **One bucket for anonymous traffic.** All unauthenticated requests share a single
  accounting bucket; each authenticated user has their own.

### Rollout is staged

The first step runs the metering in *observe mode*: it records what each request
would consume and whether it would be allowed, but always issues the link, under
one flat limit for all tiers. This gathers real usage before any enforcement or
per-tier limits are turned on. The entry point already returns the allow/deny
decision — callers simply don't act on it yet. Later steps enforce it and split the
limits by tier.
