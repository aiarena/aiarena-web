import { useMemo, useState } from "react";
import { graphql, useFragment } from "react-relay";

import { DevelopersContent_viewer$key } from "./__generated__/DevelopersContent_viewer.graphql";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import CodeBlock from "@/_components/_display/CodeBlock";
import TokenReveal from "@/_components/_actions/TokenReveal";
import RegenerateTokenButton from "@/_components/_actions/RegenerateTokenButton";
import TabNav from "@/_components/_nav/TabNav";
import SquareButton from "@/_components/_actions/SquareButton";
import LanguagePicker from "@/_components/_actions/LanguagePicker";
import Pitch from "./Pitch";
import { reverseUrl } from "@/_lib/reverseUrl";

const TOKEN_PLACEHOLDER = "<your token>";
const ROUND_ID_PLACEHOLDER = "<paste a round id from example 2>";

// language=GraphQL
const EXAMPLE_1_QUERY = `{
  viewer {
    user {
      username
    }
  }
}`;

// language=GraphQL
const EXAMPLE_2_QUERY = `{
  competitions(status: OPEN) {
    edges {
      node {
        id
        name
        rounds {
          edges {
            node {
              id
              complete
              number
            }
          }
        }
      }
    }
  }
}`;

// language=GraphQL
const EXAMPLE_3_QUERY = `query ($id: ID!) {
  node(id: $id) {
    ... on RoundsType {
      id
      number
      finished
      matches {
        edges {
          node {
            result {
              type
            }
            participant1 {
              name
            }
            participant2 {
              name
            }
          }
        }
      }
    }
  }
}`;

// language=YAML
const IDE_CONFIG_YAML = `schema: https://aiarena.net/graphql/
documents:
  - "**/*.{ts,tsx,graphql}"
  - "**/*.py"`;

// language=Python
const PYTHON_NODES_HELPER = `def nodes(connection):
    """Unwrap edges/node connection into a flat list."""
    if not connection:
        return []
    return [edge["node"] for edge in connection["edges"]]


# Usage:
# competitions = nodes(payload["data"]["competitions"])
# # -> [{"id": "...", "name": "..."}, ...]`;

// language=TypeScript
const TS_NODES_HELPER = `export function nodes<T>(
  connection: { edges?: ReadonlyArray<{ node: T | null } | null> } | null,
): T[] {
  return (
    connection?.edges
      ?.map((edge) => edge?.node)
      .filter((node): node is T => node != null) ?? []
  );
}

// Usage:
// const competitions = nodes(data.competitions);
// // -> [{ id: "...", name: "..." }, ...]`;

// Note: no \`language=\` annotation — PyCharm would lint the __SLOT__ placeholders as undefined identifiers.
const PYTHON_TEMPLATE = `import requests

query = """
__QUERY__
"""
__VARIABLES_BLOCK__
response = requests.post(
    "https://aiarena.net/graphql/",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Token __TOKEN__",
    },
    json=__JSON_FIELD__,
)

payload = response.json()
print(payload["data"])`;

const NODE_TEMPLATE = `const query = \`
__QUERY__
\`;
__VARIABLES_BLOCK__
const response = await fetch("https://aiarena.net/graphql/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Token __TOKEN__",
  },
  body: __BODY_FIELD__,
});

const { data, errors } = await response.json();
console.log(data);`;

const CURL_TEMPLATE = `curl https://aiarena.net/graphql/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token __TOKEN__" \\
  -d '__BODY__'`;

function fillTemplate(template: string, slots: Record<string, string>): string {
  return Object.entries(slots).reduce(
    (acc, [key, value]) => acc.split(key).join(value),
    template,
  );
}

interface Example {
  name: string;
  blurb: string;
  query: string;
  variables?: Record<string, string>;
  showConnectionsNote?: boolean;
}

function buildExamples(sampleRoundId: string | null): Example[] {
  return [
    {
      name: "1. Who am I?",
      blurb:
        "Smallest possible query. If user is null, your auth header is wrong. Otherwise, you're logged in.",
      query: EXAMPLE_1_QUERY,
    },
    {
      name: "2. Active rounds",
      blurb:
        "First taste of Relay connections and filters. Grab any round id from the result for example 3.",
      query: EXAMPLE_2_QUERY,
      showConnectionsNote: true,
    },
    {
      name: "3. Matches in a round",
      blurb:
        "Uses node(id: $id) — the universal lookup. Same root field works for any object with an id; the fragment spread picks which fields you want. Variable passed in the request body.",
      query: EXAMPLE_3_QUERY,
      variables: {
        id: sampleRoundId ?? ROUND_ID_PLACEHOLDER,
      },
    },
  ];
}

interface LanguageOption {
  display: string;
  shikiLang: "python" | "javascript" | "bash";
  render: (example: Example, token: string) => string;
}

function renderPython(example: Example, token: string): string {
  const hasVariables = example.variables != null;
  return fillTemplate(PYTHON_TEMPLATE, {
    __QUERY__: example.query,
    __TOKEN__: token,
    __VARIABLES_BLOCK__: hasVariables
      ? `\nvariables = ${JSON.stringify(example.variables, null, 4)}\n`
      : "",
    __JSON_FIELD__: hasVariables
      ? '{"query": query, "variables": variables}'
      : '{"query": query}',
  });
}

function renderNode(example: Example, token: string): string {
  const hasVariables = example.variables != null;
  const queryLiteral = example.query
    .replace(/\\/g, "\\\\")
    .replace(/`/g, "\\`");
  return fillTemplate(NODE_TEMPLATE, {
    __QUERY__: queryLiteral,
    __TOKEN__: token,
    __VARIABLES_BLOCK__: hasVariables
      ? `\nconst variables = ${JSON.stringify(example.variables, null, 2)};\n`
      : "",
    __BODY_FIELD__: hasVariables
      ? "JSON.stringify({ query, variables })"
      : "JSON.stringify({ query })",
  });
}

function renderCurl(example: Example, token: string): string {
  const hasVariables = example.variables != null;
  const body = hasVariables
    ? { query: example.query, variables: example.variables }
    : { query: example.query };
  // Escape single quotes for shell
  const shellSafeBody = JSON.stringify(body).replace(/'/g, "'\\''");
  return fillTemplate(CURL_TEMPLATE, {
    __TOKEN__: token,
    __BODY__: shellSafeBody,
  });
}

const LANGUAGES: LanguageOption[] = [
  { display: "Python", shikiLang: "python", render: renderPython },
  { display: "Node.js", shikiLang: "javascript", render: renderNode },
  { display: "curl", shikiLang: "bash", render: renderCurl },
];

function playgroundUrl(example: Example): string {
  const parts = [`query=${encodeURIComponent(example.query)}`];
  if (example.variables) {
    parts.push(
      `variables=${encodeURIComponent(
        JSON.stringify(example.variables, null, 2),
      )}`,
    );
  }
  return `${reverseUrl("graphql")}#${parts.join("&")}`;
}

interface DevelopersContentProps {
  viewer: DevelopersContent_viewer$key | null;
  isLoggedIn: boolean;
  sampleRoundId: string | null;
}

export default function DevelopersContent({
  viewer,
  isLoggedIn,
  sampleRoundId,
}: DevelopersContentProps) {
  const data = useFragment(
    graphql`
      fragment DevelopersContent_viewer on Viewer {
        apiToken
        ...TokenReveal_viewer
        ...RegenerateTokenButton_viewer
      }
    `,
    viewer,
  );

  const examples = useMemo(() => buildExamples(sampleRoundId), [sampleRoundId]);
  const [activeExample, setActiveExample] = useState(examples[0].name);

  const example = examples.find((e) => e.name === activeExample) ?? examples[0];
  const tokenForSnippet = data?.apiToken ?? TOKEN_PLACEHOLDER;

  return (
    <div className="max-w-5xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="font-gugi text-4xl pb-2">AI Arena APIs</h1>
        <p className="text-gray-300 max-w-2xl mx-auto">
          AI Arena exposes a GraphQL API and a legacy REST API. We recommend
          GraphQL for new integrations — it's what we're investing in going
          forward.
        </p>
      </div>

      <WrappedTitle title="GraphQL" font="font-bold" />

      <div className="grid md:grid-cols-3 gap-4 mb-6 text-sm">
        <Pitch
          title="Interactive playground"
          body="The /graphql/ endpoint ships an in-browser playground with autocomplete and live docs. Try queries with your own credentials."
          href={reverseUrl("graphql")}
          linkText="Open playground →"
        />
        <Pitch
          title="Fewer requests"
          body="Fetch deeply nested data in one round-trip. Things that would take 1600 REST requests can be a single query."
        />
        <Pitch
          title="Only what you ask for"
          body="Request only the fields you need. Less bandwidth, less load on our database, less parsing on your end."
        />
      </div>

      <div className="bg-darken-2 border border-neutral-600 rounded-md p-4 mb-8">
        <h3 className="text-base font-semibold mb-2">Your API token</h3>
        {isLoggedIn && data ? (
          <>
            <TokenReveal viewer={data} />
            <RegenerateTokenButton viewer={data} outerClassName="mt-2" />
            <p className="text-xs text-gray-400 mt-2">
              For non-browser clients (scripts, servers, bots), send it as the{" "}
              <span className="font-mono">Authorization: Token &lt;key&gt;</span>{" "}
              header. The same token works for both GraphQL and REST.
            </p>
          </>
        ) : (
          <p className="text-sm text-gray-300">
            <a href={reverseUrl("login")} className="underline">
              Log in
            </a>{" "}
            to see your personal API token. The examples below use{" "}
            <span className="font-mono">{TOKEN_PLACEHOLDER}</span> as a
            placeholder.
          </p>
        )}
      </div>

      <h3 className="text-lg font-semibold mb-3">Try a query</h3>

      <TabNav
        tabs={examples.map((e) => ({ name: e.name, href: "#" }))}
        activeTab={activeExample}
        setActiveTab={setActiveExample}
      />

      <div className="bg-darken-2 border border-neutral-600 border-t-0 rounded-b-md p-4 mb-6">
        <p className="text-sm text-gray-300 mb-3">{example.blurb}</p>

        <CodeBlock code={example.query} lang="graphql" />

        {example.variables ? (
          <div className="mt-3">
            <p className="text-xs text-gray-400 mb-1">Variables</p>
            <CodeBlock
              code={JSON.stringify(example.variables, null, 2)}
              lang="json"
            />
            {sampleRoundId == null ? (
              <p className="text-xs text-yellow-400 mt-1">
                No live round id available — run example 2 and paste an id
                here.
              </p>
            ) : null}
          </div>
        ) : null}

        {example.showConnectionsNote ? (
          <details className="mt-3 text-sm text-gray-300 bg-darken-3 border border-neutral-700 rounded-md">
            <summary className="cursor-pointer select-none px-3 py-2 hover:text-white">
              What's with the edges / node nesting?
            </summary>
            <div className="px-3 pb-3 pt-1 border-t border-neutral-700 space-y-2">
              <p>
                Lists of related objects come back as{" "}
                <strong>connections</strong>, not plain arrays. A connection
                holds <span className="font-mono">edges</span>,{" "}
                <span className="font-mono">node</span>, and{" "}
                <span className="font-mono">pageInfo</span> — that's where
                cursor-based pagination, the cursor itself,{" "}
                <span className="font-mono">totalCount</span>, and other
                per-connection metadata go. A plain list has nowhere to put
                that.
              </p>
              <p>
                Single root entities skip the wrapper — that's why{" "}
                <span className="font-mono">viewer</span> in example 1 and{" "}
                <span className="font-mono">node(id: $id)</span> in example 3
                return fields directly. Only one-to-many fields get the
                connection shape.
              </p>
              <p>
                Worth writing a one-line unwrap helper once and using it
                everywhere:
              </p>
              <div className="!mt-3">
                <LanguagePicker
                  options={[
                    {
                      display: "Python",
                      code: PYTHON_NODES_HELPER,
                      lang: "python",
                    },
                    {
                      display: "TypeScript",
                      code: TS_NODES_HELPER,
                      lang: "typescript",
                    },
                  ]}
                />
              </div>
              <p>
                Full spec:{" "}
                <a
                  href="https://relay.dev/graphql/connections.htm"
                  className="underline"
                  target="_blank"
                  rel="noopener"
                >
                  Relay Cursor Connections
                </a>
                .
              </p>
            </div>
          </details>
        ) : null}

        <div className="mt-4">
          <SquareButton
            onClick={() =>
              window.open(playgroundUrl(example), "_blank", "noopener")
            }
            text="Try in Playground →"
          />
          <p className="text-xs text-gray-400 mt-2">
            The playground runs at <span className="font-mono">/graphql/</span>{" "}
            and authenticates with your{" "}
            <strong>existing browser session</strong> — no token, no copy-paste.
            It's the same session you used to log into this page, so anything
            you can see in the UI you can query here.
          </p>
        </div>
      </div>

      <h3 className="text-lg font-semibold mb-3">…or call it from code</h3>
      <p className="text-sm text-gray-300 mb-3">
        A GraphQL client library is optional. It's a POST to{" "}
        <span className="font-mono">/graphql/</span> with a JSON body
        containing <span className="font-mono">query</span> and (optionally)
        <span className="font-mono"> variables</span>. Your token lives in the{" "}
        <span className="font-mono">Authorization</span> header.
      </p>

      <div className="bg-darken-2 border border-neutral-600 rounded-md p-4 mb-10">
        <LanguagePicker
          options={LANGUAGES.map((l) => ({
            display: l.display,
            code: l.render(example, tokenForSnippet),
            lang: l.shikiLang,
          }))}
        />
        {isLoggedIn ? (
          <p className="text-xs text-gray-400 mt-2">
            This snippet uses your real API token. Keep it secret — anyone with
            it can act as you.
          </p>
        ) : null}
      </div>

      <h3 className="text-lg font-semibold mb-2">Recommended client libraries</h3>
      <p className="text-sm text-gray-300 mb-2">
        You don't need any of these to call the API — the snippets above use
        only the standard library. But for non-trivial integrations, a real
        client is more pleasant.
      </p>
      <ul className="list-disc list-inside text-sm text-gray-300 mb-6 space-y-1">
        <li>
          <strong>Python:</strong>{" "}
          <a
            href="https://gql.readthedocs.io/"
            className="underline"
            target="_blank"
            rel="noopener"
          >
            gql
          </a>{" "}
          — sync and async, supports subscriptions, multiple transports.
        </li>
        <li>
          <strong>Node.js / TypeScript:</strong>{" "}
          <a
            href="https://github.com/jasonkuhrt/graphql-request"
            className="underline"
            target="_blank"
            rel="noopener"
          >
            graphql-request
          </a>{" "}
          — minimal, no caching or React. Just{" "}
          <span className="font-mono">request(url, query, variables)</span>.
        </li>
        <li>
          <strong>TypeScript with typed queries:</strong> pair the above with{" "}
          <a
            href="https://the-guild.dev/graphql/codegen"
            className="underline"
            target="_blank"
            rel="noopener"
          >
            GraphQL Code Generator
          </a>{" "}
          — generates types straight from our schema.
        </li>
      </ul>

      <h3 className="text-lg font-semibold mb-2">IDE autocomplete</h3>
      <p className="text-sm text-gray-300 mb-2">
        Most editors support GraphQL autocomplete and inline schema docs via a
        small config file. Drop this <span className="font-mono">graphql.config.yml</span>{" "}
        at the root of any project that talks to our API — your IDE will fetch
        the schema directly from us, no local checkout needed:
      </p>
      <CodeBlock code={IDE_CONFIG_YAML} lang="yaml" className="mb-2" />
      <p className="text-xs text-gray-400 mb-6">
        Works with the JetBrains GraphQL plugin (PyCharm, IntelliJ, WebStorm)
        and the{" "}
        <a
          href="https://marketplace.visualstudio.com/items?itemName=GraphQL.vscode-graphql"
          className="underline"
          target="_blank"
          rel="noopener"
        >
          VS Code GraphQL extension
        </a>
        . Once installed, you get autocomplete, hover docs, and validation in
        any <span className="font-mono">.graphql</span> file or string literal.
      </p>

      <h3 className="text-lg font-semibold mb-2">Learn more</h3>
      <ul className="list-disc list-inside text-sm text-gray-300 mb-10 space-y-1">
        <li>
          <a href={reverseUrl("graphql")} className="underline" target="_blank">
            Interactive playground
          </a>{" "}
          — autocomplete, schema browser, run real queries
        </li>
        <li>
          <a
            href="https://graphql.org/learn/"
            className="underline"
            target="_blank"
            rel="noopener"
          >
            GraphQL.org — Introduction to GraphQL
          </a>{" "}
          — the language itself: queries, variables, fragments, mutations
        </li>
        <li>
          <a
            href="https://relay.dev/graphql/connections.htm"
            className="underline"
            target="_blank"
            rel="noopener"
          >
            Relay Cursor Connections spec
          </a>{" "}
          — our list fields follow this shape (<span className="font-mono">edges</span>,{" "}
          <span className="font-mono">node</span>, <span className="font-mono">pageInfo</span>)
        </li>
        <li>
          <span className="text-gray-400">
            Tip: every object also has a <span className="font-mono">databaseId</span>{" "}
            (integer) alongside the opaque <span className="font-mono">id</span>, if
            you need a legacy-style numeric id.
          </span>
        </li>
      </ul>

      <div className="bg-darken-2 border border-customGreen/40 rounded-md p-4 mb-10">
        <h3 className="text-base font-semibold mb-2">
          Stuck? Want to chat about it?
        </h3>
        <p className="text-sm text-gray-300">
          Ping <span className="font-mono">@ipeterov</span> in the{" "}
          <a
            href="https://discord.gg/Emm5Ztz"
            className="underline"
            target="_blank"
            rel="noopener"
          >
            AI Arena Discord
          </a>
          . Happy to help port an existing REST integration over, do a bit of
          pair programming, or extend the API if you need something it doesn't
          expose yet. Not just a polite offer — I actually love talking about
          this stuff.
        </p>
      </div>

      <WrappedTitle title="REST (legacy)" font="font-bold" />

      <div className="text-sm text-gray-300 space-y-3 mb-6">
        <p>
          The REST API is still supported. New endpoints land in GraphQL first,
          and we may eventually deprecate REST — building new integrations on
          GraphQL will save you a migration later.
        </p>
        <p>It uses the same API token as GraphQL.</p>
        <ul className="list-disc list-inside space-y-1">
          <li>
            <a href={reverseUrl("api-root")} className="underline" target="_blank">
              Browsable API root
            </a>
          </li>
          <li>
            <a href={reverseUrl("schema-swagger-ui")} className="underline" target="_blank">
              Swagger reference
            </a>
          </li>
          <li>
            <a href="/wiki/data-api/" className="underline" target="_blank">
              Data API wiki
            </a>{" "}
            — narrative docs and integration notes
          </li>
        </ul>
      </div>
    </div>
  );
}

