# aiarena

## `urls.py` is the source of truth for navigation

`urls.py` defines every URL the app can navigate to — for both the Django views
*and* the React SPA. Routes that only render in React still get a named entry
here, pointing at the SPA-serving view.

**Every frontend-reachable route must have a `name=`.** Two reasons:

- The SPA generates typed URL helpers from these names (see
  `frontend-spa/CLAUDE.md`), so a link to a renamed or deleted route becomes a
  compile error instead of a production 404. An unnamed route can't be reversed,
  so the frontend would have to hand-build the path — which is what we're
  avoiding.
- A path the SPA renders but that *isn't* declared here 404s on hard refresh /
  direct navigation, because the request reaches Django before React loads. So a
  new client-side route in `App.tsx` needs a matching named route here, served by
  the frontend view.

Catch-all patterns (e.g. a `re_path` covering a whole SPA subtree) are fine as a
hard-refresh safety net, but they can't be `reverse()`d to a specific path — so
keep an explicit named entry alongside them for any sub-path the app links to.

The generator (`core/management/commands/generate_url_definitions.py`) derives
each path from `reverse()` itself rather than reconstructing it, so the generated
URLs can't drift from Django's routing. When you change a route, rerun
`uv run dev pre-commit` to regenerate, and keep that guarantee intact if you
touch the generator.
