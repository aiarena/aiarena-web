import { ResultsFilters } from "./BotResultsTable";
import { CoreBotRaceLabelChoices } from "../__generated__/InformationSection_bot.graphql";
import { CoreMatchParticipationResultCauseChoices, CoreMatchParticipationResultChoices } from "./__generated__/BotResultsTbody_bot.graphql";
import { HardcodedMatchTypeOptions } from "../CustomOptions/MatchTypeOptions";
import { cleanStr, setOrDelete, setPair, toBool, toNum } from "@/_lib/searchParamsUtils";
import { getBase64FromID, getIDFromBase64 } from "@/_lib/relayHelpers";


export const BotResultsTableSortingMap: Record<string, string> = {
    id: "id",
    date: "match__result__created",
};

export const BOT_RESULTTABLE_SORT_KEY = "sort";

const DEFAULTS = {
    includeStarted: false,
    includeQueued: false,
    includeFinished: true,
} as const;

export function encodeFiltersToSearchParams(
    filters: ResultsFilters,
    prev: URLSearchParams,
) {
    const searchParam = new URLSearchParams(prev);

    setPair(
        searchParam,
        "opponentId",
        cleanStr(getIDFromBase64(filters.opponentId, "BotType")),
        "opponentName",
        cleanStr(filters.opponentName),
    );
    setPair(
        searchParam,
        "opponentRace",
        cleanStr(filters.opponentPlaysRaceId),
        "opponentRaceName",
        cleanStr(filters.opponentPlaysRaceName),
    );
    setPair(
        searchParam,
        "competitionId",
        cleanStr(getIDFromBase64(filters.competitionId, "CompetitionType")),
        "competitionName",
        cleanStr(filters.competitionName),
    );

    // strings
    setOrDelete(searchParam, "result", cleanStr(filters.result)?.toLowerCase());
    setOrDelete(searchParam, "cause", cleanStr(filters.cause)?.toLowerCase());
    setOrDelete(searchParam, "matchType", cleanStr(filters.matchType)?.toLowerCase());
    setOrDelete(searchParam, "mapName", cleanStr(filters.mapName));
    setOrDelete(searchParam, "after", cleanStr(filters.matchStartedAfter));
    setOrDelete(searchParam, "before", cleanStr(filters.matchStartedBefore));
    setOrDelete(searchParam, "tags", cleanStr(filters.tags));

    // numbers
    setOrDelete(
        searchParam,
        "avgStepMin",
        filters.avgStepTimeMin == null ? undefined : String(filters.avgStepTimeMin),
    );
    setOrDelete(
        searchParam,
        "avgStepMax",
        filters.avgStepTimeMax == null ? undefined : String(filters.avgStepTimeMax),
    );
    setOrDelete(
        searchParam,
        "gameTimeMin",
        filters.gameTimeMin == null ? undefined : String(filters.gameTimeMin),
    );
    setOrDelete(
        searchParam,
        "gameTimeMax",
        filters.gameTimeMax == null ? undefined : String(filters.gameTimeMax),
    );

    // booleans: if different from defaults
    if (filters.includeQueued !== DEFAULTS.includeQueued)
        searchParam.set("queued", filters.includeQueued ? "1" : "0");
    else searchParam.delete("queued");

    if (filters.includeStarted !== DEFAULTS.includeStarted)
        searchParam.set("started", filters.includeStarted ? "1" : "0");
    else searchParam.delete("started");

    if (filters.includeFinished !== DEFAULTS.includeFinished)
        searchParam.set("finished", filters.includeFinished ? "1" : "0");
    else searchParam.delete("finished");

    // optional booleans: store only when true
    if (filters.searchOnlyMyTags) searchParam.set("myTags", "1");
    else searchParam.delete("myTags");

    if (filters.showEveryonesTags) searchParam.set("allTags", "1");
    else searchParam.delete("allTags");

    return searchParam;
}

export function decodeFiltersFromSearchParams(
    searchParam: URLSearchParams,
    preset?: { competitionId?: string; competitionName?: string },
): ResultsFilters {
    const rawCompetitionId = searchParam.get("competitionId");

    const competitionId = rawCompetitionId && rawCompetitionId.trim() !== ""
        ? getBase64FromID(rawCompetitionId, "CompetitionType")
        : preset?.competitionId

    const competitionName =
        cleanStr(searchParam.get("competitionName")) ?? preset?.competitionName;

    const rawOpponentId = searchParam.get("opponentId");
    const opponentId =
        rawOpponentId && rawOpponentId.trim() !== ""
            ? getBase64FromID(rawOpponentId, "BotType")
            : null;


    return {
        opponentId: cleanStr(opponentId),
        opponentName: cleanStr(searchParam.get("opponentName")),

        opponentPlaysRaceId: cleanStr(searchParam.get("opponentRace")) as CoreBotRaceLabelChoices | undefined,
        opponentPlaysRaceName: cleanStr(searchParam.get("opponentRaceName")) as CoreMatchParticipationResultCauseChoices | undefined,

        result: (cleanStr(searchParam.get("result"))?.toUpperCase()) as CoreMatchParticipationResultChoices | undefined ?? undefined,
        cause: (cleanStr(searchParam.get("cause"))?.toUpperCase()) as CoreMatchParticipationResultCauseChoices | undefined ?? undefined,

        avgStepTimeMin: toNum(searchParam.get("avgStepMin")),
        avgStepTimeMax: toNum(searchParam.get("avgStepMax")),
        gameTimeMin: toNum(searchParam.get("gameTimeMin")),
        gameTimeMax: toNum(searchParam.get("gameTimeMax")),

        matchType: (cleanStr(searchParam.get("matchType"))?.toUpperCase()) as HardcodedMatchTypeOptions | undefined ?? undefined,
        mapName: cleanStr(searchParam.get("mapName")),

        competitionId: cleanStr(competitionId) ?? undefined,
        competitionName: cleanStr(competitionName) ?? undefined,

        matchStartedAfter: cleanStr(searchParam.get("after")),
        matchStartedBefore: cleanStr(searchParam.get("before")),

        tags: cleanStr(searchParam.get("tags")),
        searchOnlyMyTags: searchParam.get("myTags") === "1" ? true : undefined,
        showEveryonesTags: searchParam.get("allTags") === "1" ? true : undefined,

        includeStarted: toBool(searchParam.get("started"), DEFAULTS.includeStarted),
        includeQueued: toBool(searchParam.get("queued"), DEFAULTS.includeQueued),
        includeFinished: toBool(searchParam.get("finished"), DEFAULTS.includeFinished),
    };
}
