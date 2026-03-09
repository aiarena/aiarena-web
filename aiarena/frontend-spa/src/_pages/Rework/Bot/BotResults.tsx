import { useParams, useSearchParams } from "react-router";

import { Suspense, useCallback, useMemo } from "react";

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
import { getBase64FromID } from "@/_lib/relayHelpers";
import { graphql, useLazyLoadQuery } from "react-relay";
import FetchError from "@/_components/_display/FetchError";
import { BotResultsQuery } from "./__generated__/BotResultsQuery.graphql";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";

export default function BotResults() {
  const { botId } = useParams<{ botId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();

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

  const urlFilters = useMemo(
    () => decodeFiltersFromSearchParams(searchParams),
    [searchParams],
  );

  const urlOrderBy = useMemo(() => {
    const s = urlSorting?.[0];
    if (!s) return "-match__result__created";
    const backendField = BotResultsTableSortingMap[s.id] ?? "id";
    return s.desc ? `-${backendField}` : backendField;
  }, [urlSorting]);

  const resultData = useLazyLoadQuery<BotResultsQuery>(
    graphql`
      query BotResultsQuery(
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

  if (!resultData.node) {
    return <FetchError type="bot" />;
  }

  return (
    <Suspense
      key={botId}
      fallback={<DisplaySkeleton height={1200} styles={SkeletonCardShadow} />}
    >
      <BotResultsTable
        data={resultData.node}
        onApplyFilters={applyFiltersToUrl}
        onApplySort={applySortingToUrl}
        initialFilters={urlFilters}
        initialSorting={urlSorting}
      />
    </Suspense>
  );
}
