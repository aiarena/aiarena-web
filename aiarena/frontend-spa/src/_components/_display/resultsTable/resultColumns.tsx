import { useMemo } from "react";
import { graphql, readInlineData } from "react-relay";
import { Link } from "react-router";
import { createColumnHelper } from "@tanstack/react-table";
import { ArrowDownCircleIcon } from "@heroicons/react/24/outline";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { getMatchResultParsed } from "@/_lib/parseMatchResult";
import timeAgoShort from "@/_lib/timeAgoSort";
import { formatGameTime } from "@/_lib/formatGameTime";
import ResultBotCell from "./ResultBotCell";
import {
  resultColumns_result$data,
  resultColumns_result$key,
} from "./__generated__/resultColumns_result.graphql";

/**
 * The columns of a results table (match, both bots with their ELO change,
 * result, duration, age, replay), shared by every table that lists results.
 *
 * A table spreads `...resultColumns_result` on each result node, turns the
 * nodes into rows with `readResultRow`, and renders `useResultColumns()`.
 * The fragment is @inline so rows can be read outside React hooks.
 */
export type ResultRow = resultColumns_result$data;

export function readResultRow(result: resultColumns_result$key): ResultRow {
  return readInlineData(
    graphql`
      fragment resultColumns_result on ResultType @inline {
        id
        created
        type
        replayFile
        gameTimeFormatted
        winner {
          name
        }
        participant1 {
          eloChange
          match {
            id
          }
          bot {
            id
            name
          }
        }
        participant2 {
          eloChange
          bot {
            id
            name
          }
        }
      }
    `,
    result,
  );
}

const columnHelper = createColumnHelper<ResultRow>();

export function useResultColumns() {
  return useMemo(
    () => [
      columnHelper.accessor((row) => row.participant1?.match.id, {
        id: "id",
        header: "Match ID",
        enableSorting: false,
        cell: (info) => {
          const matchId = getIDFromBase64(info.getValue(), "MatchType");
          if (!matchId) {
            return null;
          }
          return (
            <Link
              className="font-semibold text-gray-200 truncate mr-2"
              to={reverseUrl("match", { pk: matchId })}
              role="cell"
              aria-label={`View match details for Result ID ${info.getValue()}`}
              title={matchId}
            >
              {matchId}
            </Link>
          );
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant1?.bot.name || "", {
        id: "participant1",
        header: "Bot",
        enableSorting: false,
        cell: (info) => (
          <ResultBotCell participant={info.row.original.participant1} winnerName={info.row.original.winner?.name} />
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.participant2?.bot.name || "", {
        id: "participant2",
        header: "Opponent",
        enableSorting: false,
        cell: (info) => (
          <ResultBotCell participant={info.row.original.participant2} winnerName={info.row.original.winner?.name} />
        ),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.type ?? "", {
        id: "type",
        header: "Result",
        enableSorting: false,
        cell: (info) => {
          const result = getMatchResultParsed(
            info.getValue(),
            info.row.original.participant1?.bot.name,
            info.row.original.participant2?.bot.name,
          );
          return result != "" ? result : "In Queue";
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => formatGameTime(row.gameTimeFormatted ?? ""), {
        id: "gameTimeFormatted",
        header: "Duration",
        enableSorting: false,
        cell: (info) => info.getValue(),
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.created ?? "", {
        id: "created",
        header: "Created",
        enableSorting: false,
        cell: (info) => {
          const rawTime = info.getValue();
          return rawTime ? `${timeAgoShort(rawTime)} ago` : "In Queue";
        },
        meta: { priority: 1 },
      }),
      columnHelper.accessor((row) => row.replayFile || "", {
        id: "replayFile",
        header: "Replay",
        enableSorting: false,
        cell: (info) => {
          const replayFile = info.getValue();
          if (!replayFile) {
            return "";
          }
          return (
            <span className="flex justify-between">
              <Link
                className="font-semibold text-gray-200 truncate mr-2"
                to={replayFile}
                role="cell"
                aria-label={`Get Replay for ${getIDFromBase64(info.row.original.id, "ResultType")}`}
                title="Download"
              >
                <span className="flex items-center gap-1">
                  <ArrowDownCircleIcon height={18} /> Replay
                </span>
              </Link>
            </span>
          );
        },
        meta: { priority: 1 },
      }),
    ],
    [],
  );
}
