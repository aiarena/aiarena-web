import type { ReactNode } from "react";

import { TrophyCheckResult } from "./adminCompetitionTypes";

interface TrophyStatusMessageProps {
  result: TrophyCheckResult;
}

export default function TrophyStatusMessage({
  result,
}: TrophyStatusMessageProps) {
  if (result.status === "idle") {
    return null;
  }

  if (result.status === "loading") {
    return (
      <section className="rounded-sm border-2 border-neutral-600 bg-darken-4 p-4 shadow-lg shadow-black">
        <p className="font-semibold text-gray-200">Checking trophies…</p>

        <p className="mt-1 text-sm text-gray-400">
          Comparing the competition rankings, award set, and existing trophies.
        </p>
      </section>
    );
  }

  const styles = getStatusStyles(result.status);

  return (
    <section
      className={`rounded-sm border-2 bg-darken-4 p-4 shadow-lg shadow-black ${styles.border}`}
    >
      <div className="border-b border-neutral-700 pb-3">
        <p className={`font-semibold ${styles.title}`}>
          {result.message ?? getDefaultMessage(result.status)}
        </p>
      </div>

      {result.status !== "error" && (
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <ResultCount
            label="Expected"
            value={result.expectedTrophyCount}
            borderClass="border-neutral-600"
          />

          <ResultCount
            label="Existing"
            value={result.existingTrophyCount}
            borderClass="border-neutral-600"
          />

          <ResultCount
            label="Missing"
            value={result.missingTrophyCount}
            borderClass={
              (result.missingTrophyCount ?? 0) > 0
                ? "border-orange-500"
                : "border-customGreen"
            }
          />

          <ResultCount
            label="Incorrect"
            value={result.incorrectTrophyCount}
            borderClass={
              (result.incorrectTrophyCount ?? 0) > 0
                ? "border-red-500"
                : "border-customGreen"
            }
          />
        </div>
      )}

      {result.issues && result.issues.length > 0 && (
        <StatusSection
          title="Issues"
          borderClass="border-red-500"
          titleClass="text-red-400"
        >
          <ul className="space-y-2 text-sm text-gray-200">
            {result.issues.map((issue, index) => (
              <li
                key={`${index}-${issue}`}
                className="rounded-sm border border-neutral-700 bg-darken-4 px-3 py-2"
              >
                {issue}
              </li>
            ))}
          </ul>
        </StatusSection>
      )}

      {result.incorrectTrophies && result.incorrectTrophies.length > 0 && (
        <StatusSection
          title="Incorrect trophies"
          borderClass="border-red-500"
          titleClass="text-red-400"
        >
          <div className="space-y-3">
            {result.incorrectTrophies.map((trophy) => (
              <IncorrectTrophyCard key={trophy.id} trophy={trophy} />
            ))}
          </div>
        </StatusSection>
      )}

      {!result.incorrectTrophies?.length &&
        result.incorrectTrophyIds &&
        result.incorrectTrophyIds.length > 0 && (
          <StatusSection
            title="Incorrect trophy IDs"
            borderClass="border-red-500"
            titleClass="text-red-400"
          >
            <div className="flex flex-wrap gap-2">
              {result.incorrectTrophyIds.map((id) => (
                <span
                  key={id}
                  className="rounded-sm border border-red-500 bg-darken-4 px-3 py-1 font-mono text-sm text-red-300"
                >
                  {id}
                </span>
              ))}
            </div>
          </StatusSection>
        )}

      {result.missingTrophies && result.missingTrophies.length > 0 && (
        <StatusSection
          title="Missing trophies"
          borderClass="border-orange-500"
          titleClass="text-orange-400"
        >
          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px] text-left text-sm">
              <thead className="border-b border-neutral-600 bg-darken-4">
                <tr>
                  <TableHeader>Rank</TableHeader>
                  <TableHeader>Bot</TableHeader>
                  <TableHeader>Condition</TableHeader>
                  <TableHeader>Icon</TableHeader>
                </tr>
              </thead>

              <tbody className="divide-y divide-neutral-700">
                {result.missingTrophies.map((trophy) => (
                  <tr
                    key={`${trophy.botId}-${trophy.condition}`}
                    className="bg-darken-2 transition-colors hover:bg-darken-4"
                  >
                    <TableCell>
                      <span className="font-semibold text-orange-300">
                        {trophy.rank}
                      </span>
                    </TableCell>

                    <TableCell>
                      <span className="font-semibold text-gray-100">
                        {trophy.botName}
                      </span>
                    </TableCell>

                    <TableCell>
                      <CodeValue value={trophy.condition} />
                    </TableCell>

                    <TableCell>{trophy.iconName}</TableCell>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </StatusSection>
      )}
    </section>
  );
}

function IncorrectTrophyCard({
  trophy,
}: {
  trophy: NonNullable<TrophyCheckResult["incorrectTrophies"]>[number];
}) {
  return (
    <article className="rounded-sm border border-neutral-600 bg-darken-4 shadow-sm shadow-black">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-700 px-4 py-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Trophy #{trophy.id}
          </p>

          <p className="mt-1 font-semibold text-gray-100">{trophy.botName}</p>
        </div>

        <ParticipationBadge
          participated={trophy.participated}
          placement={trophy.placement}
        />
      </header>

      <div className="grid gap-4 p-4 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
        <div>
          <DetailLabel>Name</DetailLabel>

          <p className="mt-1 break-words text-sm text-gray-200">
            {trophy.name}
          </p>
        </div>

        <div>
          <DetailLabel>Competition</DetailLabel>

          <p className="mt-1 text-sm text-gray-200">{trophy.competitionName}</p>
        </div>

        <div className="md:min-w-44">
          <DetailLabel>Icon</DetailLabel>

          <div className="mt-2 flex items-center gap-3">
            {trophy.iconImage ? (
              <img
                src={trophy.iconImage}
                alt={trophy.iconName ?? "Trophy icon"}
                className="h-10 w-10 rounded-sm border border-neutral-600 bg-darken-2 object-contain p-1"
              />
            ) : (
              <div className="flex h-10 w-10 items-center justify-center rounded-sm border border-neutral-600 bg-darken-2 text-xs text-gray-500">
                None
              </div>
            )}

            <span className="text-sm font-medium text-gray-200">
              {trophy.iconName ?? "No icon"}
            </span>
          </div>
        </div>
      </div>

      <footer className="flex flex-wrap gap-3 border-t border-neutral-700 bg-darken-2 px-4 py-3">
        <MetadataValue
          label="Condition"
          value={trophy.conditionDisplay || trophy.condition || "Unset"}
        />

        <MetadataValue
          label="Condition key"
          value={trophy.condition || "unset"}
          code
        />

        <MetadataValue label="Bot ID" value={trophy.botId} code />

        <MetadataValue
          label="Competition ID"
          value={trophy.competitionId || ""}
          code
        />
      </footer>
    </article>
  );
}

function ParticipationBadge({
  participated,
  placement,
}: {
  participated: boolean;
  placement: number | null;
}) {
  if (!participated) {
    return (
      <span className="inline-flex rounded-sm border border-red-500 px-3 py-1 text-xs font-semibold text-red-400">
        Did not participate
      </span>
    );
  }

  return (
    <span className="inline-flex rounded-sm border border-customGreen px-3 py-1 text-xs font-semibold text-customGreen">
      Participated · Place {placement ?? "unknown"}
    </span>
  );
}

function MetadataValue({
  label,
  value,
  code = false,
}: {
  label: string;
  value: string;
  code?: boolean;
}) {
  return (
    <div className="flex items-center gap-2 rounded-sm border border-neutral-700 bg-darken-4 px-3 py-2">
      <span className="text-xs font-semibold text-gray-500">{label}</span>

      <span className={`text-xs text-gray-200 ${code ? "font-mono" : ""}`}>
        {value}
      </span>
    </div>
  );
}

function CodeValue({ value }: { value: string }) {
  return (
    <code className="rounded-sm border border-neutral-700 bg-darken-4 px-2 py-1 text-xs text-gray-200">
      {value}
    </code>
  );
}

function DetailLabel({ children }: { children: ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
      {children}
    </p>
  );
}

function ResultCount({
  label,
  value,
  borderClass,
}: {
  label: string;
  value: number | undefined;
  borderClass: string;
}) {
  return (
    <div
      className={`rounded-sm border bg-darken-2 px-4 py-3 shadow-sm shadow-black ${borderClass}`}
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
        {label}
      </p>

      <p className="mt-1 text-xl font-bold text-gray-100">{value ?? 0}</p>
    </div>
  );
}

function StatusSection({
  title,
  borderClass,
  titleClass,
  children,
}: {
  title: string;
  borderClass: string;
  titleClass: string;
  children: ReactNode;
}) {
  return (
    <div className={`mt-4 rounded-sm border bg-darken-2 p-4 ${borderClass}`}>
      <p className={`mb-3 font-semibold ${titleClass}`}>{title}</p>

      {children}
    </div>
  );
}

function TableHeader({ children }: { children: ReactNode }) {
  return (
    <th className="whitespace-nowrap px-3 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
      {children}
    </th>
  );
}

function TableCell({ children }: { children: ReactNode }) {
  return <td className="px-3 py-3 text-gray-300">{children}</td>;
}

function getStatusStyles(
  status: Exclude<TrophyCheckResult["status"], "idle" | "loading">,
) {
  const styles = {
    incomplete: {
      border: "border-red-500",
      title: "text-red-400",
    },
    not_awarded: {
      border: "border-orange-500",
      title: "text-orange-400",
    },
    awarded: {
      border: "border-customGreen",
      title: "text-customGreen",
    },
    error: {
      border: "border-red-500",
      title: "text-red-400",
    },
  };

  return styles[status];
}

function getDefaultMessage(
  status: Exclude<TrophyCheckResult["status"], "idle" | "loading">,
) {
  const messages = {
    incomplete: "Trophies are incomplete or incorrect.",
    not_awarded: "Trophies have not been awarded.",
    awarded: "Trophies have been awarded.",
    error: "The trophy check could not be completed.",
  };

  return messages[status];
}
