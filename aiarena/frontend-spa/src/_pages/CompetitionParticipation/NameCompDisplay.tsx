import { getBase64FromID, getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Link } from "react-router";
import { NameCompDisplayQuery } from "./__generated__/NameCompDisplayQuery.graphql";

export default function NameCompDisplay({ id }: { id: string }) {
  const data = useLazyLoadQuery<NameCompDisplayQuery>(
    graphql`
      query NameCompDisplayQuery($id: ID!) {
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
          }
        }
        viewer {
          user {
            patreonLevel
          }
        }
      }
    `,
    { id: getBase64FromID(id!, "CompetitionParticipationType") || "" },
  );

  const participation = data?.node;
  if (!participation?.bot || !participation?.competition) {
    return null;
  }
  const { bot, competition } = participation;

  return (
    <div className="flex items-center justify-between  bg-darken-2 lg:bg-transparent">
      <h3 className="text-lg font-semibold text-gray-100">
        <Link
          to={reverseUrl("bot", { pk: getIDFromBase64(bot.id, "BotType") })}
          className="font-semibold"
        >
          {bot.name}
        </Link>{" "}
        on{" "}
        <Link
          to={reverseUrl("competition", {
            pk: getIDFromBase64(competition.id, "CompetitionType"),
          })}
          className="font-semibold"
        >
          {competition.name}
        </Link>
      </h3>
    </div>
  );
}
