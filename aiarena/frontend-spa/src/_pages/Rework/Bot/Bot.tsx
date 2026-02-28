import { graphql, useLazyLoadQuery } from "react-relay";
import InformationSection from "./InformationSection";
import { BotQuery } from "./__generated__/BotQuery.graphql";
import { useParams, useSearchParams } from "react-router";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense, useCallback, useMemo, useState } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import BotCompetitionsTable from "./BotCompetitionsTable";
import FetchError from "@/_components/_display/FetchError";
import { BotResultQuery } from "./__generated__/BotResultQuery.graphql";
import BotResultsTable, {
  ResultsFilters,
} from "./BotResultsTable/BotResultsTable";
import {
  BOT_RESULTTABLE_SORT_KEY,
  BotResultsTableSortingMap,
  decodeFiltersFromSearchParams,
  encodeFiltersToSearchParams,
} from "./BotResultsTable/botResultTableSearchParams";
import { SortingState } from "@tanstack/react-table";
import {
  decodeSortingFromSearchParams,
  encodeSortingToSearchParams,
} from "@/_lib/searchParamsUtils";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";

export default function Bot() {
  const { botId } = useParams<{ botId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const [onlyActive, setOnlyActive] = useState(false);
  const id = getBase64FromID(botId!, "BotType") || "";

  const allowedSortIds = useMemo(() => new Set(["id", "date"]), []);

  const urlSorting = useMemo(
    () =>
      decodeSortingFromSearchParams(
        searchParams,
        allowedSortIds,
        BOT_RESULTTABLE_SORT_KEY,
      ),
    [searchParams, allowedSortIds],
  );

  const data = useLazyLoadQuery<BotQuery>(
    graphql`
      query BotQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            ...InformationSection_bot
            ...BotCompetitionsTable_bot
          }
        }
      }
    `,
    { id: getBase64FromID(botId!, "BotType") || "" },
  );

  const urlFilters = useMemo(
    () => decodeFiltersFromSearchParams(searchParams),
    [searchParams],
  );

  const urlOrderBy = useMemo(() => {
    const s = urlSorting?.[0];
    if (!s) return "-id";
    const backendField = BotResultsTableSortingMap[s.id] ?? "id";
    return s.desc ? `-${backendField}` : backendField;
  }, [urlSorting]);

  const resultData = useLazyLoadQuery<BotResultQuery>(
    graphql`
      query BotResultQuery(
        $id: ID!
        $cursor: String
        $first: Int!
        $orderBy: String!
        $opponentId: String
        $opponentPlaysRace: String
        $result: String
        $cause: String
        $avgStepTimeMin: Decimal
        $avgStepTimeMax: Decimal
        $gameTimeMin: Decimal
        $gameTimeMax: Decimal
        $matchType: String
        $mapName: String
        $competitionId: String
        $matchStartedAfter: DateTime
        $matchStartedBefore: DateTime
        $tags: String
        $searchOnlyMyTags: Boolean
        $showEveryonesTags: Boolean
        $includeStarted: Boolean
        $includeQueued: Boolean
        $includeFinished: Boolean
      ) {
        node(id: $id) {
          ... on BotType {
            ...BotResultsTbody_bot
              @arguments(
                cursor: $cursor
                first: $first
                orderBy: $orderBy
                opponentId: $opponentId
                opponentPlaysRace: $opponentPlaysRace
                result: $result
                cause: $cause
                avgStepTimeMin: $avgStepTimeMin
                avgStepTimeMax: $avgStepTimeMax
                gameTimeMin: $gameTimeMin
                gameTimeMax: $gameTimeMax
                matchType: $matchType
                mapName: $mapName
                competitionId: $competitionId
                matchStartedAfter: $matchStartedAfter
                matchStartedBefore: $matchStartedBefore
                tags: $tags
                searchOnlyMyTags: $searchOnlyMyTags
                showEveryonesTags: $showEveryonesTags
                includeStarted: $includeStarted
                includeQueued: $includeQueued
                includeFinished: $includeFinished
              )
          }
        }
      }
    `,
    {
      id,
      cursor: null,
      first: 50,
      orderBy: urlOrderBy,

      opponentId: urlFilters.opponentId,
      opponentPlaysRace: urlFilters.opponentPlaysRaceId,
      result: urlFilters.result?.toLowerCase(),
      cause: urlFilters.cause?.toLowerCase(),
      avgStepTimeMin: urlFilters.avgStepTimeMin ?? null,
      avgStepTimeMax: urlFilters.avgStepTimeMax ?? null,
      gameTimeMin: urlFilters.gameTimeMin,
      gameTimeMax: urlFilters.gameTimeMax,
      matchType: urlFilters.matchType?.toLowerCase(),
      mapName: urlFilters.mapName,
      competitionId: urlFilters.competitionId,
      matchStartedAfter: urlFilters.matchStartedAfter,
      matchStartedBefore: urlFilters.matchStartedBefore,
      tags: urlFilters.tags,
      searchOnlyMyTags: urlFilters.searchOnlyMyTags ?? false,
      showEveryonesTags: urlFilters.showEveryonesTags ?? false,
      includeStarted: urlFilters.includeStarted ?? false,
      includeQueued: urlFilters.includeQueued ?? false,
      includeFinished: urlFilters.includeFinished ?? true,
    },
  );

  const applyFiltersToUrl = useCallback(
    (next: ResultsFilters, replace = false) => {
      const nextSearchParam = encodeFiltersToSearchParams(next, searchParams);
      setSearchParams(nextSearchParam, { replace });
    },
    [searchParams, setSearchParams],
  );
  const applySortingToUrl = useCallback(
    (next: SortingState, replace = false) => {
      const nextSearchParam = encodeSortingToSearchParams(
        next,
        searchParams,
        BOT_RESULTTABLE_SORT_KEY,
      );
      setSearchParams(nextSearchParam, { replace });
    },
    [searchParams, setSearchParams],
  );

  if (!data.node || !resultData.node) {
    return <FetchError type="bot" />;
  }

  return (
    <>
      <div className="max-w-7xl mx-auto">
        <h4 className="mb-4">Bot information</h4>
        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <InformationSection bot={data.node} />
        </Suspense>
        <h4 className="mb-4">Competition Participations</h4>
        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <BotCompetitionsTable
            bot={data.node}
            onlyActive={onlyActive}
            appendHeader={
              <div
                className="flex gap-4 items-center"
                role="group"
                aria-label="Bot filtering controls"
              >
                <div className="flex items-center gap-2">
                  <label
                    htmlFor="downloadable-toggle"
                    className="text-sm font-medium text-gray-300"
                  >
                    Only active
                  </label>
                  <SimpleToggle
                    enabled={onlyActive}
                    onChange={() => setOnlyActive(!onlyActive)}
                  />
                </div>
              </div>
            }
          />
        </Suspense>
      </div>
      <h4 className="mb-4 mt-8">Results</h4>
      <Suspense fallback={<LoadingSpinner color="light-gray" />}>
        <BotResultsTable
          data={resultData.node}
          onApplyFilters={applyFiltersToUrl}
          onApplySort={applySortingToUrl}
          initialFilters={urlFilters}
          initialSorting={urlSorting}
        />
      </Suspense>
    </>
  );
}
