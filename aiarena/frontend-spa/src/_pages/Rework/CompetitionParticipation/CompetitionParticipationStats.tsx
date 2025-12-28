import { graphql, useLazyLoadQuery } from "react-relay";
import { CompetitionParticipationStatsQuery } from "./__generated__/CompetitionParticipationStatsQuery.graphql";
import MapStatsTable from "./MapStatsTable";
import MatchupStatsTable from "./MatchupStatsTable";
import { getBase64FromID } from "@/_lib/relayHelpers";
import LoadingDots from "@/_components/_display/LoadingDots";
import { Suspense, useState } from "react";
import { statsSideNavbarLinks } from "./StatsSideNavbarLinks";
import WithStatsSideButtons from "@/_components/_nav/WithStatsSideButtons";

interface CompetitionParticipationStatsProps {
  id: string;
}

export default function CompetitionParticipationStats(
  props: CompetitionParticipationStatsProps
) {
  const [activeTab, setActiveTab] =
    useState<(typeof statsSideNavbarLinks)[number]["state"]>("overview");
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
            ...MapStatsTable_node
            ...MatchupStatsTable_node
          }
        }
      }
    `,
    { id: getBase64FromID(props.id!, "CompetitionParticipationType") || "" }
  );

  return (
    <Suspense fallback={<LoadingDots />}>
      {data?.node ? (
        <WithStatsSideButtons activeTab={activeTab} setActiveTab={setActiveTab}>
          {activeTab === "overview" && <p>overview</p>}
          {activeTab === "bots" && <MapStatsTable data={data.node} />}
          {activeTab === "maps" && <MatchupStatsTable data={data.node} />}
        </WithStatsSideButtons>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-400">Competition participation not found</p>
        </div>
      )}
    </Suspense>
  );
}
