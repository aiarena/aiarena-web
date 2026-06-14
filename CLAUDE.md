# CLAUDE.md

## Working in this codebase

### The task is keeping the codebase buildable, not just shipping the feature

Every session is locally scoped, so there's a strong pull toward the one-off solution: the shim, the near-duplicate helper, the slightly-different convention you reached for because you didn't go read how the neighboring code already did it. Each of those closes the turn cleanly and looks done — but none of it is *locally* wrong, so the incoherence accumulates in the seams, invisible at the altitude you're working at, until the next feature is the one that doesn't fit and quietly doesn't get started.

So weight your decisions accordingly. Refactoring to make a change fit cleanly — including splitting an overgrown module or component into smaller self-contained ones — is in-scope by default; it does not need permission, and the bigger diff is not the thing to minimize. The cost of an unnecessary refactor is visible and easy to veto in review; the cost of leaving a seam is invisible and compounds. Bias toward doing the structural work now, while it's cheap. The one thing to preserve is legibility: refactor freely, but stay loud about what you consolidated and why, so the change can be vetoed if you reshaped something that mattered.

**What this looks like in practice.** If you're partway through a planned change and discover that doing item N *properly* needs a refactor larger than the rest of the plan combined — that's the moment the pull toward a hack is strongest and exactly the wrong instinct. The discovery that the refactor is large is the signal it's load-bearing. So: **stop and surface it** (don't quietly take the shortcut), explain what you hit, agree on the approach, then **do it in full** rather than leaving the seam half-open.

Don't blindly agree with everything suggested. If you think an alternative is better, say so.

### Write down architectural reasoning in a local CLAUDE.md, not in comments

When you find yourself explaining the *why* behind a structure — the idea a package is built around, a boundary it must not cross, an invariant, or a "we tried X and it was a mistake" — prefer a `CLAUDE.md` in that package over burying the reasoning in a code comment. A local file is read whenever anyone works in that directory, so it's where the conceptual map belongs, and it's what lets the next session notice when a quick hack is about to diverge from the original intent.

Explain the *concept* and the boundaries; **don't name concrete files/classes/functions** — names drift, but the idea should survive refactors. For "where is X right now", the code is the source of truth.

### No false "backward compatibility"

Do NOT keep old code around "for backward compatibility" without verifying it's actually needed — that's tech debt, not safety. We have no public APIs, so the only legitimate case is database schema (migrations run before code updates — see `aiarena/core/models/CLAUDE.md`).

Before renaming or replacing anything, **grep for usages of the old name** — it takes seconds. If nothing uses it, delete it immediately. If things use it, migrate them in the same session. Broken state mid-refactor is expected and fine: import errors are how you find the remaining usages. Don't add shims to "fix" the broken state — the fix is to finish migrating.

## Before committing

Run `uv run dev pre-commit` to run all checks. This is what CI runs, so if it passes here it should pass there.

It runs Ruff (check + format), regenerates the GraphQL schema (`aiarena/schema.graphql`) from the Python types, runs the Relay compiler, and runs ESLint + `tsc`. Because it regenerates the schema from the Python source, it's relevant to **backend** changes too, not just frontend. Don't run `ruff`, `eslint`, `tsc`, or `relay-compiler` directly — this command sequences them correctly.

## Scratch files — never use `/tmp`

NEVER write to `/tmp` (or any system temp dir, including via `tempfile`) for scratch files, downloads, intermediate output, or test artifacts. It's too easy to litter there and hard to find anything useful later. Write to `.scratch/` in the repo root instead — it's the project's effective `/tmp` (gitignored).

When cloning an external repo for inspection, clone it into the repo root here, NOT into `/tmp`. Inside the project root the normal Read/Grep/Glob tools work directly; outside it you're stuck shelling out.

## Debugging: recognize your limitations

You don't have access to logs, runtime state, or real-time debugging tools — the developer has significantly more debugging capability than you do, and many issues need information you simply can't access. When you hit that wall, say so and ask for the specific thing you need ("this looks like X or Y — could you check [specific thing]?") rather than emitting a confident guess. Asking for more info is collaborative, not annoying.
