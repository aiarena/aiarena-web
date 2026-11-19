import { graphql, useLazyLoadQuery } from "react-relay";
import RoundsSection from "./RoundsSection";
import { RoundsQuery } from "./__generated__/RoundsQuery.graphql";
import { getBase64FromID } from "@/_lib/relayHelpers";
import { useParams } from "react-router";
import FetchError from "@/_components/_display/FetchError";
export default function Rounds() {
  const { roundId } = useParams<{ roundId: string }>();
  const data = useLazyLoadQuery<RoundsQuery>(
    graphql`
      query RoundsQuery($id: ID!) {
        node(id: $id) {
          ... on RoundsType {
            ...RoundsSection_round
          }
        }
      }
    `,
    { id: getBase64FromID(roundId!, "RoundsType") || "" }
  );

  if (!data.node) {
    return <FetchError type="round" />;
  }

  return (
    <>
      <RoundsSection data={data.node} />
    </>
  );
}
