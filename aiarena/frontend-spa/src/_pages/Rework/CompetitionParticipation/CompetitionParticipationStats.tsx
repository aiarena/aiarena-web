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
        query CompetitionParticipationStatsResultsQuery($id: ID!) {
          node(id: $id) {
            ... on CompetitionParticipationType {
              id
              bot {
                ...BotResultsTable_bot
              }
            }
          }
        }
      `,
      { id: getBase64FromID(props.id!, "CompetitionParticipationType") || "" }
    );

  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <div className="px-2 pb-8">
        {data?.node && data?.node.bot ? (
          <>
            {props.activeTab === "overview" && (
              <>
                {props.activeTopTab === "elograph" && (
                  <EloChart data={data.node} />
                )}
                {props.activeTopTab === "winsbytime" && (
                  <WinsByTime data={data.node} />
                )}
                {props.activeTopTab === "winsbyrace" && (
                  <RaceMatchup data={data.node} />
                )}
              </>
            )}
            {props.activeTab === "maps" && <MapStatsTable data={data.node} />}
            {props.activeTab === "matchups" && (
              <MatchupStatsTable data={data.node} />
            )}

            {props.activeTab === "results" &&
              (resultsData.node && resultsData.node.bot ? (
                <BotResultsTable data={resultsData.node.bot} />
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
