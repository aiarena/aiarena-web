import { Dispatch, SetStateAction } from "react";
import Modal from "@/_components/_actions/Modal";
import SectionDivider from "@/_components/_display/SectionDivider";
import clsx from "clsx";
import { ResultsFilters } from "../BotResultsTable";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ResultsFiltersModalQuery } from "./__generated__/ResultsFiltersModalQuery.graphql";
import BotSearchList from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/BotSearchList";
import MapSearchList from "@/_pages/UserMatchRequests/UserMatchRequests/_modals/MapSearchList";
import CompetitionSearchList from "./CompetitionSearchList";
import MainButton from "@/_components/_actions/MainButton";
import SearchList from "@/_components/_actions/SearchList";
import { raceOptions } from "../CustomOptions/BotRaceOptions";
import { resultOptions } from "../CustomOptions/ResultOptions";

import { CoreBotRaceLabelChoices } from "../__generated__/InformationSection_bot.graphql";
import { resultCauseOptions } from "../CustomOptions/ResultCauseOptions";
import {
  HardcodedMatchTypeOptions,
  matchTypeOptions,
} from "../CustomOptions/MatchTypeOptions";
import {
  CoreMatchParticipationResultCauseChoices,
  CoreMatchParticipationResultChoices,
} from "../__generated__/BotResultsTbody_bot.graphql";

interface ResultsFiltersModalProps {
  isOpen: boolean;
  onClose: () => void;
  filters: ResultsFilters;
  setFilters: Dispatch<SetStateAction<ResultsFilters>>;
  onApply: (next: ResultsFilters) => void;
}

export default function ResultsFiltersModal({
  isOpen,
  onClose,
  filters,
  setFilters,
  onApply,
}: ResultsFiltersModalProps) {
  const data = useLazyLoadQuery<ResultsFiltersModalQuery>(
    graphql`
      query ResultsFiltersModalQuery {
        ...BotSearchList
        ...MapSearchList
        ...CompetitionSearchList
      }
    `,
    {},
  );

  const handleChange =
    (key: keyof ResultsFilters) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const value = e.target.value;
      if (key === "avgStepTimeMin" || key === "avgStepTimeMax") {
        setFilters((prev: ResultsFilters) => ({
          ...prev,
          [key]: value === "" ? undefined : Number(value),
        }));
      } else if (key === "gameTimeMin" || key === "gameTimeMax") {
        setFilters((prev: ResultsFilters) => ({
          ...prev,
          [key]: value === "" ? undefined : Number(value),
        }));
      } else {
        setFilters((prev: ResultsFilters) => ({
          ...prev,
          [key]: value,
        }));
      }
    };

  const handleApply = () => {
    onApply(filters);
    onClose();
  };

  const handleClear = () => {
    setFilters((oldF) => ({
      ...oldF,

      opponentName: undefined,
      opponentId: undefined,
      opponentPlaysRaceId: undefined,
      opponentPlaysRaceName: undefined,
      result: undefined,
      cause: undefined,
      avgStepTimeMin: undefined,
      avgStepTimeMax: undefined,
      gameTimeMin: undefined,
      gameTimeMax: undefined,
      matchType: undefined,
      mapName: undefined,

      tags: undefined,
      searchOnlyMyTags: undefined,
      showEveryonesTags: undefined,

      matchStartedAfter: undefined,
      matchStartedBefore: undefined,
    }));
  };
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Filter results">
      <form
        className="flex flex-col gap-6"
        onSubmit={(e) => {
          e.preventDefault();
          handleApply();
        }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Opponent */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-opponent-label"
          >
            <label id="filter-opponent-label" className="font-medium">
              Opponent
            </label>
            <BotSearchList
              value={{
                name: filters.opponentName || "",
                id: filters.opponentId || "",
              }}
              setValue={(val) => {
                setFilters((f: ResultsFilters) => ({
                  ...f,
                  opponentName: val?.name,
                  opponentId: val?.id,
                }));
              }}
              relayRootQuery={data}
            />
          </div>

          {/* Opponent Race */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-opponent-race-label"
          >
            <label id="filter-opponent-race-label" className=" font-medium">
              Opponent Race
            </label>
            <SearchList
              value={{
                id: filters.opponentPlaysRaceId || "",
                name: filters.opponentPlaysRaceName,
              }}
              setValue={(option) =>
                setFilters((f: ResultsFilters) => ({
                  ...f,
                  opponentPlaysRaceId:
                    (option?.id as CoreBotRaceLabelChoices) || "",
                  opponentPlaysRaceName: (option?.name as string) || "",
                }))
              }
              setQuery={() => {}}
              displayValue={(value) =>
                (value as { id: CoreBotRaceLabelChoices; name: string })
                  ?.name || ""
              }
              options={raceOptions}
              placeholder="Type to search races..."
            />
          </div>

          {/* Result */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-result-label"
          >
            <label className="font-medium" id="filter-result-label">
              Result
            </label>

            <SearchList
              value={{ id: filters.result || "" }}
              setValue={(option) =>
                setFilters((f) => ({
                  ...f,
                  result: (option?.id ??
                    "") as CoreMatchParticipationResultChoices,
                }))
              }
              setQuery={() => {}}
              displayValue={(value) => {
                const displayVal = resultOptions.find(
                  (i) => i.id === value?.id,
                );

                if (displayVal) {
                  return displayVal.name;
                } else {
                  return "";
                }
              }}
              options={resultOptions}
              placeholder="Any result..."
            />
          </div>

          {/* Cause */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-cause-label"
          >
            <label id="filter-cause-label" className="font-medium">
              Result Cause
            </label>

            <SearchList
              value={{ id: filters.cause || "" }}
              setValue={(option) =>
                setFilters((f) => ({
                  ...f,
                  cause: (option?.id ??
                    "") as CoreMatchParticipationResultCauseChoices,
                }))
              }
              setQuery={() => {}}
              displayValue={(value) => {
                const displayVal = resultCauseOptions.find(
                  (i) => i.id === value?.id,
                );

                if (displayVal) {
                  return displayVal.name;
                } else {
                  return "";
                }
              }}
              options={resultCauseOptions}
              placeholder="Any result cause..."
            />
          </div>
        </div>

        <SectionDivider color="gray" className="pb-1" />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Avg Step (ms) min */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-avgstep-min-label"
          >
            <label
              id="filter-avgstep-min-label"
              htmlFor="filter-avgstep-min"
              className="font-medium"
            >
              Minimum Avg Step (ms)
            </label>
            <input
              id="filter-avgstep-min"
              type="number"
              value={filters.avgStepTimeMin ?? ""}
              onChange={handleChange("avgStepTimeMin")}
              className="rounded-lg border px-3 py-2"
              placeholder="e.g. 0"
              min={0}
            />
          </div>

          {/* Avg Step (ms) max */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-avgstep-max-label"
          >
            <label
              id="filter-avgstep-max-label"
              htmlFor="filter-avgstep-max"
              className="font-medium"
            >
              Maximum Avg Step (ms)
            </label>
            <input
              id="filter-avgstep-max"
              type="number"
              value={filters.avgStepTimeMax ?? ""}
              onChange={handleChange("avgStepTimeMax")}
              className="rounded-lg border px-3 py-2"
              placeholder="e.g. 250"
              min={0}
            />
          </div>

          {/* Game Time */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-gametime-label"
          >
            <label
              id="filter-gametime-min-label"
              htmlFor="filter-gametime-min"
              className="font-medium"
            >
              Minimum Game Time (seconds)
            </label>
            <input
              id="filter-gametime-min"
              type="number"
              value={filters.gameTimeMin ?? ""}
              onChange={handleChange("gameTimeMin")}
              className="rounded-lg border px-3 py-2"
              placeholder="e.g. 0"
              min={0}
            />
          </div>

          {/* Game Time (seconds) max */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-gametime-max-label"
          >
            <label
              id="filter-gametime-max-label"
              htmlFor="filter-gametime-max"
              className="font-medium"
            >
              Maximum Game Time (seconds)
            </label>
            <input
              id="filter-gametime-max"
              type="number"
              value={filters.gameTimeMax ?? ""}
              onChange={handleChange("gameTimeMax")}
              className="rounded-lg border px-3 py-2"
              placeholder="e.g. 250"
              min={0}
            />
          </div>
        </div>
        <SectionDivider color="gray" className="pb-1" />
        {/* DateTime filter */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Match Started After */}
          <div className="flex flex-col gap-1">
            <label
              htmlFor="matchStartedAfter"
              className="font-medium text-gray-200"
            >
              Match Started After
            </label>
            <input
              id="matchStartedAfter"
              type="datetime-local"
              value={
                filters.matchStartedAfter
                  ? filters.matchStartedAfter.slice(0, 16)
                  : ""
              }
              onChange={(e) => {
                const val = e.target.value;
                setFilters((prev) => ({
                  ...prev,
                  matchStartedAfter: val ? `${val}:00Z` : undefined,
                }));
              }}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-900 text-gray-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-customGreen"
            />
          </div>

          {/* Match Started Before */}
          <div className="flex flex-col gap-1">
            <label
              htmlFor="matchStartedBefore"
              className="font-medium text-gray-200"
            >
              Match Started Before
            </label>
            <input
              id="matchStartedBefore"
              type="datetime-local"
              value={
                filters.matchStartedBefore
                  ? filters.matchStartedBefore.slice(0, 16)
                  : ""
              }
              onChange={(e) => {
                const val = e.target.value;
                setFilters((prev) => ({
                  ...prev,
                  matchStartedBefore: val ? `${val}:00Z` : undefined,
                }));
              }}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-900 text-gray-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-customGreen"
            />
          </div>
        </div>
        <SectionDivider color="gray" className="pb-1" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Match Type */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-matchtype-label"
          >
            <label id="filter-matchtype-label" className=" font-medium">
              Match Origin
            </label>
            <SearchList
              value={{ id: filters.matchType || "" }}
              setValue={(option) =>
                setFilters((f) => ({
                  ...f,
                  matchType: (option?.id ?? "") as HardcodedMatchTypeOptions,
                }))
              }
              setQuery={() => {}}
              displayValue={(value) => {
                const displayVal = matchTypeOptions.find(
                  (i) => i.id === value?.id,
                );

                if (displayVal) {
                  return displayVal.name;
                } else {
                  return "";
                }
              }}
              options={matchTypeOptions}
              placeholder="Any match origin..."
            />
          </div>

          {/* Map */}
          <div
            className="flex flex-col gap-1"
            role="group"
            aria-labelledby="filter-map-label"
          >
            <label className="flex flex-col gap-1">
              <span className="font-medium">Map</span>
              <MapSearchList
                value={{
                  id: filters.mapName || "",
                  name: filters.mapName || "",
                }}
                setValue={(val) => {
                  setFilters((f: ResultsFilters) => ({
                    ...f,
                    mapName: val?.name,
                  }));
                }}
                relayRootQuery={data}
              />
            </label>
          </div>

          {/* Competition */}
          <div
            className="flex flex-col gap-1 md:col-span-2"
            role="group"
            aria-labelledby="filter-competition-label"
          >
            <label className="flex flex-col gap-1">
              <span className="font-medium">Competition</span>
              <CompetitionSearchList
                value={{
                  id: filters.competitionId || "",
                  name: filters.competitionName || "",
                }}
                setValue={(val) =>
                  setFilters((f: ResultsFilters) => ({
                    ...f,
                    competitionId: val?.id,
                    competitionName: val?.name,
                  }))
                }
                relayRootQuery={data}
              />
            </label>
          </div>
        </div>
        <SectionDivider color="gray" className="pb-1" />

        {/* Tags */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1 md:col-span-2">
            <label className="font-medium">Tags</label>
            <input
              type="text"
              value={filters.tags ?? ""}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  tags: e.target.value === "" ? undefined : e.target.value,
                }))
              }
              className="w-full rounded-lg border border-neutral-700 bg-neutral-900 text-gray-100 px-3 py-2"
              placeholder="comma,separated,tags"
            />
          </div>

          <label className="flex items-center gap-2 select-none">
            <input
              type="checkbox"
              checked={filters.showEveryonesTags ?? false}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  showEveryonesTags: e.target.checked,
                }))
              }
              className="h-4 w-4 rounded border-neutral-700 bg-neutral-900"
            />
            <span className="text-sm text-gray-200">
              Show Everyone&apos;s Tags
            </span>
          </label>

          <label className="flex items-center gap-2 select-none">
            <input
              type="checkbox"
              checked={filters.searchOnlyMyTags ?? false}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  searchOnlyMyTags: e.target.checked,
                }))
              }
              className="h-4 w-4 rounded border-neutral-700 bg-neutral-900"
            />
            <span className="text-sm text-gray-200">Search Only My Tags</span>
          </label>
        </div>

        <SectionDivider color="gray" className="pb-1" />

        <div className="flex flex-col sm:flex-row justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={handleClear}
            className="mx-4 my-2 text-smtransition hover:underline"
          >
            Clear all
          </button>

          <MainButton
            type="submit"
            className={clsx(
              "px-4 py-2 text-sm rounded-xl font-medium",
              "bg-customGreen text-black hover:bg-customGreen/90 transition",
            )}
            text="Apply filters"
          />
        </div>
      </form>
    </Modal>
  );
}
