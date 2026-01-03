import { getBase64FromID, getIDFromBase64 } from "@/_lib/relayHelpers";
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
    { id: getBase64FromID(id!, "CompetitionParticipationType") || "" }
  );

  return (
    <div className="flex items-center justify-between pt-6 pl-6 md:pb-0 pb-6 bg-darken-2 lg:bg-transparent">
      <h3 className="text-lg font-semibold text-gray-100">
        <Link
          to={`/bots/${getIDFromBase64(data?.node?.bot?.id, "BotType")}`}
          className="font-semibold"
        >
          {data?.node?.bot?.name}
        </Link>{" "}
        on{" "}
        <Link
          to={`/competitions/${getIDFromBase64(
            data?.node?.competition?.id,
            "CompetitionType"
          )}`}
          className="font-semibold"
        >
          {data?.node?.competition?.name}
        </Link>
      </h3>
    </div>
  );
}
