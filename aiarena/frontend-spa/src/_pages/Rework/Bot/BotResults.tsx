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

import { SortingState, VisibilityState } from "@tanstack/react-table";

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

import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

type Props = {
  botZipUpdated: string;
  botId?: string;
  origin?: "bot" | "competition";
  competition?: {
    id: string;
    name: string;
  };
};

export default function BotResults({
  botZipUpdated,
  botId,
  origin = "bot",
  competition,
}: Props) {
  const { botId: routeBotId } = useParams<{
    botId: string;
  }>();

  const [searchParams, setSearchParams] = useSearchParams();

  const [sinceUpdated, setSinceUpdated] =
    useStateWithLocalStorage<VisibilityState>(
      "Bot_BotResultsTable_SinceUpdated",
      {},
    );

  const id = botId ?? getBase64FromID(routeBotId ?? "", "BotType") ?? "";

  const competitionId =
    origin === "competition" && competition?.id ? competition.id : undefined;

  const filterPreset = useMemo(
    () =>
      competitionId
        ? {
            competitionId,
            competitionName: competition?.name,
          }
        : undefined,
    [competitionId, competition?.name],
  );

  const allowedSortIds = useMemo(
    () =>
      origin === "competition"
        ? new Set([
            "id",
            "opponent",
            "opponent_race",
            "result",
            "elo_change",
            "cause",
            "step",
            "duration",
            "date",
            "tags",
          ])
        : new Set(["id"]),
    [origin],
  );

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
    () =>
      decodeFiltersFromSearchParams(
        searchParams,
        botZipUpdated,
        sinceUpdated?.sinceUpdated,
      ),
    [searchParams, botZipUpdated, sinceUpdated],
  );

  const effectiveFilters = useMemo<ResultsFilters>(
    () => ({
      ...urlFilters,

      ...(filterPreset
        ? {
            competitionId: filterPreset.competitionId,

            competitionName: filterPreset.competitionName,
          }
        : {}),
    }),
    [urlFilters, filterPreset],
  );

  const urlOrderBy = useMemo(() => {
    const s = urlSorting?.[0];

    if (!s) {
      return "-id";
    }

    const backendField = BotResultsTableSortingMap[s.id] ?? "-id";

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

      opponentId: effectiveFilters.opponentId || null,

      opponentPlaysRace: effectiveFilters.opponentPlaysRaceId || null,

      result: effectiveFilters.result?.toLowerCase() || null,

      cause: effectiveFilters.cause?.toLowerCase() || null,

      avgStepTimeMin: effectiveFilters.avgStepTimeMin ?? null,

      avgStepTimeMax: effectiveFilters.avgStepTimeMax ?? null,

      gameTimeMin: effectiveFilters.gameTimeMin ?? null,

      gameTimeMax: effectiveFilters.gameTimeMax ?? null,

      matchType: effectiveFilters.matchType?.toLowerCase() || null,

      mapName: effectiveFilters.mapName || null,

      competitionId: effectiveFilters.competitionId || null,

      matchStartedAfter:
        effectiveFilters.matchStartedAfter ||
        (sinceUpdated?.sinceUpdated ? botZipUpdated : null),

      matchStartedBefore: effectiveFilters.matchStartedBefore || null,

      tags: effectiveFilters.tags || null,

      searchOnlyMyTags: effectiveFilters.searchOnlyMyTags ?? false,

      showEveryonesTags: effectiveFilters.showEveryonesTags ?? false,

      includeStarted: effectiveFilters.includeStarted ?? false,

      includeQueued: effectiveFilters.includeQueued ?? false,

      includeFinished: effectiveFilters.includeFinished ?? true,
    },
  );

  const applyFiltersToUrl = useCallback(
    (next: ResultsFilters, replace = false) => {
      const filters: ResultsFilters = filterPreset
        ? {
            ...next,

            competitionId: filterPreset.competitionId,

            competitionName: filterPreset.competitionName,
          }
        : next;

      const nextSearchParam = encodeFiltersToSearchParams(
        filters,
        searchParams,
      );

      setSearchParams(nextSearchParam, {
        replace,
      });
    },
    [filterPreset, searchParams, setSearchParams],
  );

  const applySortingToUrl = useCallback(
    (next: SortingState, replace = false) => {
      const nextSearchParam = encodeSortingToSearchParams(
        next,
        searchParams,
        BOT_RESULTTABLE_SORT_KEY,
      );

      setSearchParams(nextSearchParam, {
        replace,
      });
    },
    [searchParams, setSearchParams],
  );

  if (!resultData.node) {
    return <FetchError type="bot" />;
  }

  return (
    <Suspense
      key={id}
      fallback={<DisplaySkeleton height={800} styles={SkeletonCardShadow} />}
    >
      <ErrorBoundaryWrapper>
        <BotResultsTable
          data={resultData.node}
          origin={origin}
          filterPreset={filterPreset}
          onApplyFilters={applyFiltersToUrl}
          onApplySort={applySortingToUrl}
          sinceUpdated={sinceUpdated}
          setSinceUpdated={setSinceUpdated}
          initialFilters={effectiveFilters}
          initialSorting={urlSorting}
          botZipUpdated={botZipUpdated}
        />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
