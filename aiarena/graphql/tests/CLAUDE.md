# GraphQL tests

Conventions for tests under `aiarena/graphql/tests/`. These are easy to get
subtly wrong by writing "standard pytest" instead of matching what's already
here.

## Use the `GraphQLTest` base class

Query/mutation tests subclass `GraphQLTest` (`aiarena/core/tests/base.py`) and go
through its `self.query(...)` / `self.mutate(...)` helpers, which POST to the real
GraphQL view and return the parsed `data` dict. Don't hand-roll a client or call
resolvers directly — exercise the schema end-to-end, the way a client hits it.

For a mutation test, set the query and its field name as class attributes, then
call `self.mutate(...)`:

```python
class TestRequestMatch(GraphQLTest):
    mutation_name = "requestMatch"
    mutation = """
        mutation ($input: RequestMatchInput!) {
            requestMatch(input: $input) {
                errors { messages field }
            }
        }
    """

    def test_success(self, user, bot, other_bot, map):
        self.mutate(
            login_user=user,
            variables={"input": {"bot1": self.to_global_id(BotType, bot.id), ...}},
        )
```

Useful helpers on the base class:

- **`login_user=`** — test as the actual caller. Pass nothing to test as an
  anonymous visitor (the most important case for access-control tests).
- **`self.to_global_id(SomeType, pk)`** — build the relay global ID that ID
  inputs expect. Use it; don't hand-encode base64.
- **`expected_validation_errors={field: [messages]}`** on `mutate(...)` —
  asserts the mutation's structured `errors` payload exactly.
- **`expected_errors_like=[...]`** on `query(...)` — asserts top-level GraphQL
  errors contain the given substrings.
- **`expected_status=`** — assert the HTTP status when a request should be
  rejected before resolving.

## Access-control tests: always include the anonymous case

When testing who can read or do something, cover all three callers explicitly:
the intended caller is allowed, a *different* regular user is denied, and an
*anonymous* caller (no `login_user`) is denied. The anonymous path is the one
attackers find and the one most often left untested. To test cross-user denial,
don't bake a second owner into the fixture — keep fixtures owned by the default
`user` and flip *who is asking* by passing a different `login_user`.
