import { graphql, useLazyLoadQuery } from "react-relay";
import { CompetitionParticipationStatsQuery } from "./__generated__/CompetitionParticipationStatsQuery.graphql";
import MapStatsTable from "./MapStatsTable";
import MatchupStatsTable from "./MatchupStatsTable";
import { getBase64FromID } from "@/_lib/relayHelpers";
import { Dispatch, SetStateAction, Suspense } from "react";
import {
  statsSideNavbarLinks,
  statsTopNavbarLinks,
} from "./StatsSideNavbarLinks";
import EloChart from "./EloChart";
import BotResultsTable from "../Bot/BotResultsTable";
import WinsByTime from "./WinsByTime";
import RaceMatchup from "./RaceMatchup";
import { CompetitionParticipationStatsResultsQuery } from "./__generated__/CompetitionParticipationStatsResultsQuery.graphql";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Summary from "./Summary";

type ActiveTab = (typeof statsSideNavbarLinks)[number]["state"];
type ActiveTopTab = (typeof statsTopNavbarLinks)[number]["state"];
interface CompetitionParticipationStatsProps {
  id: string;
  activeTab: ActiveTab;
  setActiveTab: Dispatch<SetStateAction<ActiveTab>>;
  activeTopTab: ActiveTopTab;
  setActiveTopTab: Dispatch<SetStateAction<ActiveTopTab>>;
}

export default function CompetitionParticipationStats(
  props: CompetitionParticipationStatsProps
) {
  const data = useLazyLoadQuery<CompetitionParticipationStatsQuery>(
    graphql`
      query CompetitionParticipationStatsQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionParticipationType {
            id
            bot {
              id
              name
            }
            competition {
              id
              name
            }
            elo
            ...EloChart_node
            ...WinsByTime_node
            ...MapStatsTable_node
            ...MatchupStatsTable_node
            ...RaceMatchup_node
            ...Summary_node
          }
        }
        viewer {
          id
        }
      }
    `,
    { id: getBase64FromID(props.id!, "CompetitionParticipationType") || "" }
  );

  const resultsData =
    useLazyLoadQuery<CompetitionParticipationStatsResultsQuery>(
      graphql`
        query CompetitionParticipationStatsResultsQuery(
          $id: ID!
          $competitionId: String
        ) {
          node(id: $id) {
            ... on CompetitionParticipationType {
              id
              bot {
                ...BotResultsTable_bot @arguments(competitionId: $competitionId)
              }
            }
          }
        }
      `,
      {
        id: getBase64FromID(props.id!, "CompetitionParticipationType") || "",
        competitionId: data?.node?.competition?.id,
      }
    );

  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <div className="px-2 pb-8">
        {data?.node && data?.node.bot ? (
          <>
            {props.activeTab === "overview" && (
              <>
                {props.activeTopTab === "elograph" && (
                  <>
                    {" "}
                    <div className="flex flex-col gap-4">
                      <EloChart data={data.node} />
                      <Summary data={data.node} />
                    </div>
                  </>
                )}
                {props.activeTopTab === "winsbytime" && (
                  <div className="flex flex-col gap-4">
                    <WinsByTime data={data.node} />
                    <Summary data={data.node} />
                  </div>
                )}
                {props.activeTopTab === "winsbyrace" && (
                  <div className="flex flex-col gap-4">
                    <RaceMatchup data={data.node} />
                    <Summary data={data.node} />
                  </div>
                )}
              </>
            )}
            {props.activeTab === "maps" && <MapStatsTable data={data.node} />}
            {props.activeTab === "matchups" && (
              <MatchupStatsTable data={data.node} />
            )}

            {props.activeTab === "results" &&
              (resultsData.node && resultsData.node.bot ? (
                <BotResultsTable
                  data={resultsData.node.bot}
                  filterPreset={{
                    competitionId: data.node.competition?.id,
                    competitionName: data.node.competition?.name,
                  }}
                />
              ) : (
                <p>Results not found</p>
              ))}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400">Competition participation not found</p>
          </div>
        )}
      </div>
    </Suspense>
  );
}
