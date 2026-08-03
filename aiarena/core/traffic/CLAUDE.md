# traffic

Who is making requests to this site, and what they cost us.

## The package owns the whole pipeline; its callers are thin

Identifying a client and recording what it cost live here, in two layers:
**classification** (what kind of client is this?) and **recording** (the Redis
bucket lifecycle). Everything outside is a thin adapter — a middleware that
measures a request and hands it over, a scheduled task that translates drained
buckets into the monitoring vendor's wire format.

Keep it that way. The shape exists to prevent the pipeline being smeared across
a middleware module and a tasks module, where the writer's key names, the
reader's sweep window and the retention TTL become three separate edits that
have to agree and nothing checks that they do.

Two boundaries worth stating outright:

- **Classification knows nothing about storage; recording knows nothing about
  the monitoring vendor.** Changing where metrics get shipped should touch the
  task and nothing else. If you find yourself importing CloudWatch (or whatever
  replaces it) inside this package, the layering has gone wrong.
- **Anything asking "is this a real person?" asks this package** rather than
  re-deriving the answer. One classifier is the whole point: before it existed
  each consumer had drifted into its own slightly different idea of what a bot
  was.

## Classification runs *after* the view

The question is answered on the way out of the middleware stack, not on the way
in. This is not a stylistic choice and it is easy to undo by accident.

The reason is that this site's most important traffic — the bots that play the
games, and people's own scripts hitting the API — is indistinguishable from a
browser by user agent. Some of it deliberately sends a browser user agent; all
of it *could*. The only reliable signal is **authentication**: which user the
request resolved to, and whether it got there via a token. That answer does not
exist until the auth stack has run, and for DRF views it isn't known until the
view itself has executed.

Classify any earlier and every authenticated class silently degrades into a
user-agent guess. Nothing errors — the graph just quietly relabels the site's
most important traffic as anonymous browser traffic and buries it in the
leftover pile. That's the failure mode to watch for if someone "tidies up" the
middleware ordering.

Two consequences that have to stay true together:

- The recording middleware must be **outermost** among the app's own
  middleware, so its post-response work sees the fully-resolved request.
- It therefore measures duration around the whole inner stack, so the timing
  metric covers real request cost rather than just view execution.

## Count *and* duration, never just count

Traffic is recorded twice per request: a count and a summed duration, under the
same class label. Both exist because they answer different questions and
disagree in the case that matters most.

Count answers "who is hitting us". Duration answers "whose requests are actually
eating the box". A client issuing a handful of pathological requests per minute
is a rounding error on a count graph — invisible next to health check volume —
while holding a large share of total request-seconds. On the duration graph it's
the tallest band on the chart. Dropping either metric as redundant loses the
ability to see that class of problem at all.

## Per-minute Redis buckets are the unit of shipping

Counts aggregate into a Redis hash per minute and a scheduled task ships them
onward. Three invariants make that work, and all are load-bearing:

- **A bucket that still exists is a minute that hasn't been shipped.** The
  emitter deletes what it sends, so "what still needs sending?" is free to
  determine and a missed run self-heals on the next one. Deleting a bucket
  before its send is confirmed turns a transient downstream failure into
  permanently lost data.
- **The bucket's key names the minute it describes**, so a late send can be
  stamped with the instant it actually happened rather than piling up at "now".
  This is what makes backfilling correct rather than merely non-crashing — which
  matters because the scheduler is genuinely down for minutes during every
  deploy.
- **A minute is drained as a whole, not metric by metric.** If anything was
  recorded for a minute, every metric ships for it, including ones that left no
  bucket of their own. Otherwise the series fall out of step: a minute whose
  durations all round to zero would vanish from the duration graph while still
  showing traffic on the count graph, which reads as a monitoring gap rather
  than as the "lots of very fast requests" it actually is.

The retention TTL and the emitter's catch-up window are deliberately the same
number. A TTL shorter than the sweep would expire the very buckets the sweep
exists to recover, and the failure is invisible: the graph just keeps its gap.
