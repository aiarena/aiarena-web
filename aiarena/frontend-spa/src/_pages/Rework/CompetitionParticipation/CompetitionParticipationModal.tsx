import Modal from "@/_components/_actions/Modal";
import MapStatsTable from "./MapStatsTable";
import MatchupStatsTable from "./MatchupStatsTable";
import { graphql, useLazyLoadQuery } from "react-relay";
import { CompetitionParticipationModalQuery } from "./__generated__/CompetitionParticipationModalQuery.graphql";
import LoadingDots from "@/_components/_display/LoadingDots";
import { Suspense } from "react";

interface CompetitionParticipationModalProps {
  isOpen: boolean;
  onClose: () => void;
  id: string;
}

export default function CompetitionParticipationModal({
  isOpen,
  onClose,
  id,
}: CompetitionParticipationModalProps) {
  const data = useLazyLoadQuery<CompetitionParticipationModalQuery>(
    graphql`
      query CompetitionParticipationModalQuery($id: ID!) {
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
    { id: id }
  );

  return (
    <>
      <Modal onClose={onClose} isOpen={isOpen} title={`Edit - "s"`} size="l">
        <Suspense fallback={<LoadingDots />}>
          {data?.node ? (
            <div className="space-y-8">
              <div className="divider">
                <span></span>
                <span>
                  <h2 className="text-2xl font-semibold">
                    {data.node.bot?.name} - {data.node.competition?.name} stats
                  </h2>
                </span>
                <span></span>
              </div>

              <MapStatsTable data={data.node} />

              <MatchupStatsTable data={data.node} />
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-400">
                Competition participation not found
              </p>
            </div>
          )}
        </Suspense>
      </Modal>
    </>
  );
}
