import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import clsx from "clsx";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { ArenaClientHeader_arenaClient$key } from "./__generated__/ArenaClientHeader_arenaClient.graphql";

interface ArenaClientHeaderProps {
  arenaClient: ArenaClientHeader_arenaClient$key;
}

const LOGO_URL = `${getPublicPrefix()}/assets_logo/ai-arena-logo.svg`;

/** The AI Arena logo. A plain <img> (inverted to white, like the navbar's)
 * rather than a CSS mask: static assets can come from another origin (the CDN
 * prefix in builds, Vite's port in dev), and browsers only apply a
 * cross-origin mask when the server sends CORS headers. Images need none. */
function ArenaLogo({ className }: { className?: string }) {
  return <img aria-hidden="true" alt="" src={LOGO_URL} className={clsx("invert", className)} />;
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-neutral-700 bg-darken-3 px-4 py-2 text-center min-w-24">
      <div className="text-2xl font-semibold text-white tabular-nums">{value.toLocaleString()}</div>
      <div className="text-xs uppercase tracking-wide text-gray-400">{label}</div>
    </div>
  );
}

export default function ArenaClientHeader(props: ArenaClientHeaderProps) {
  const client = useFragment(
    graphql`
      fragment ArenaClientHeader_arenaClient on ArenaClientType {
        username
        trusted
        owner {
          id
          username
        }
        matches1h
        matches24h
        matchesTotal
      }
    `,
    props.arenaClient,
  );

  // "Active" is inferred from recent results, not a live heartbeat.
  const active = client.matches1h > 0;

  return (
    <div className="relative overflow-hidden rounded-lg border border-neutral-800 bg-darken-2 shadow-lg shadow-black backdrop-blur p-4 sm:p-6">
      {/* Oversized, faint logo as a backdrop watermark. */}
      <ArenaLogo className="pointer-events-none absolute -right-8 -top-10 h-60 w-60 object-contain opacity-[0.05]" />

      <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center">
        <div className="relative flex h-20 w-20 shrink-0 items-center justify-center">
          <span
            className={clsx(
              "absolute inset-0 rounded-full border-2",
              active ? "border-customGreen shadow-[0_0_18px] shadow-customGreen/60" : "border-neutral-600",
            )}
          />
          <ArenaLogo
            className={clsx(
              "h-12 w-12 object-contain",
              active ? "drop-shadow-[0_0_6px_rgba(134,194,50,0.9)]" : "opacity-40",
            )}
          />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="truncate text-2xl font-semibold text-white">{client.username}</h2>
            <span
              className={clsx(
                "rounded-full border px-2 py-0.5 text-xs font-medium",
                client.trusted
                  ? "border-customGreen/60 bg-customGreen/10 text-customGreen"
                  : "border-neutral-600 bg-neutral-800 text-gray-400",
              )}
              title={
                client.trusted
                  ? "Trusted clients run ladder matches"
                  : "Untrusted clients don't run ladder matches"
              }
            >
              {client.trusted ? "Trusted" : "Untrusted"}
            </span>
          </div>
          <p className="mt-1 text-sm text-gray-300">
            Operated by{" "}
            <Link
              className="font-semibold text-gray-200"
              to={reverseUrl("author", { pk: getIDFromBase64(client.owner.id, "UserType") })}
            >
              {client.owner.username}
            </Link>
          </p>
          <p className={clsx("mt-1 text-sm", active ? "text-customGreen" : "text-gray-400")}>
            {active ? "Playing matches" : "No matches in the last hour"}
          </p>
        </div>

        {/* These count results the client submitted. The results list below
            shows every match assigned to it, which also includes matches it
            timed out on, so its length can exceed "All time". */}
        <figure>
          <figcaption className="mb-1 text-xs text-gray-400">
            Results submitted
          </figcaption>
          <div className="flex flex-wrap gap-3">
            <Stat label="Last hour" value={client.matches1h} />
            <Stat label="Last 24h" value={client.matches24h} />
            <Stat label="All time" value={client.matchesTotal} />
          </div>
        </figure>
      </div>
    </div>
  );
}
