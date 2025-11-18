import { graphql, useFragment } from "react-relay";
import RoundsTable from "./RoundsTable";
import { RoundsSection_round$key } from "./__generated__/RoundsSection_round.graphql";
import clsx from "clsx";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { getDateTimeISOString } from "@/_lib/dateUtils";

interface RoundsSectionProps {
  data: RoundsSection_round$key;
}

export default function RoundsSection(props: RoundsSectionProps) {
  const data = useFragment(
    graphql`
      fragment RoundsSection_round on RoundsType {
        competition {
          name
          id
        }
        number
        started
        finished
        ...RoundsTable_round
      }
    `,
    props.data
  );

  return (
    <section className="h-full" aria-labelledby="results-heading">
      <h2 id="results-heading" className="sr-only">
        Round {data.number}
      </h2>
      <div
        className={clsx(
          "rounded-2xl border border-neutral-800 bg-darken-2",
          "shadow-lg shadow-black p-6 sm:p-8 mb-8"
        )}
      >
        <div className="items-baseline gap-2 mb-6">
          <div className="flex">
            <h2
              id="bot-information-heading"
              className="text-xl sm:text-2xl font-semibold text-white"
            >
              Round {data.number} on{" "}
              <a
                href={`/competitions/${getIDFromBase64(data.competition.id, "CompetitionType")}`}
              >
                {" "}
                {data.competition.name}
              </a>
            </h2>
          </div>
        </div>
        <dl className="space-y-2 text-sm sm:text-base p-4">
          <div className="flex gap-2">
            <dt className="w-32 text-gray-400">Started at</dt>
            <dd className="flex-1 text-gray-100">
              {getDateTimeISOString(data.started) || "--"}
            </dd>
          </div>
          <div className="flex gap-2">
            <dt className="w-32 text-gray-400">Finished at</dt>
            <dd className="flex-1 text-gray-100">
              {getDateTimeISOString(data.finished) || "--"}
            </dd>
          </div>
        </dl>
      </div>
      <div role="region" aria-labelledby="results-table-heading">
        <h3 id="results-table-heading" className="sr-only">
          Rounds Table
        </h3>
        <RoundsTable data={data} />
      </div>
    </section>
  );
}
