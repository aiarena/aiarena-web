import { graphql, useLazyLoadQuery } from "react-relay";
import { Suspense } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { socialLinks } from "@/_data/socialLinks";

import Summary from "../Summary";
import FetchError from "@/_components/_display/FetchError";
import { useParams } from "react-router";
import RaceMatchupChart from "../RaceMatchup";
import { WinsByRaceQuery } from "./__generated__/WinsByRaceQuery.graphql";

export default function WinsByRace() {
  const { id } = useParams<{ id: string }>();
  const data = useLazyLoadQuery<WinsByRaceQuery>(
    graphql`
      query WinsByRaceQuery($id: ID!) {
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
            ...RaceMatchupChart_node
            ...Summary_node
          }
        }
        viewer {
          user {
            patreonLevel
          }
        }
      }
    `,
    { id: getBase64FromID(`${id}`, "CompetitionParticipationType") || "" },
  );

  if (!data.node || !data.node.bot) {
    return <FetchError type="competition participation" />;
  }

  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <div className="px-2 pb-8">
        {data.node.bot ? (
          <div className="flex flex-col gap-4">
            <>
              {data.viewer?.user?.patreonLevel === "NONE" ||
              data.viewer == null ? (
                <div
                  className="rounded-xl border border-neutral-800 bg-darken-2 backdrop-blur-lg shadow-lg p-4 pt-8 flex items-center justify-center"
                  style={{ height: 558 }}
                >
                  <NoItemsInListMessage className="m-auto">
                    <div className="block">
                      <p>
                        This feature is only available to Patreon Supporters
                      </p>
                      <a href={socialLinks["patreon"]} target="_blank">
                        Patreon
                      </a>
                    </div>
                  </NoItemsInListMessage>
                </div>
              ) : (
                <RaceMatchupChart data={data.node} />
              )}

              <Summary data={data.node} />
            </>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400">Competition participation not found</p>
          </div>
        )}
      </div>
    </Suspense>
  );
}
