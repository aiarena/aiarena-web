import { graphql, useLazyLoadQuery } from "react-relay";
import { getBase64FromID } from "@/_lib/relayHelpers";
import CompetitionInformationSection from "./CompetitionInformationSection";
import { useParams } from "react-router";
import FetchError from "@/_components/_display/FetchError";
import { CompetitionInformationQuery } from "./__generated__/CompetitionInformationQuery.graphql";

export default function CompetitionInformation() {
  const { competitionId } = useParams<{ competitionId: string }>();

  const data = useLazyLoadQuery<CompetitionInformationQuery>(
    graphql`
      query CompetitionInformationQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionType {
            ...CompetitionInformationSection_competition
            ...CompetitionRoundsModal_competition
          }
        }
      }
    `,
    { id: getBase64FromID(competitionId!, "CompetitionType") || "" },
  );
  if (!data.node) {
    return <FetchError type="competition" />;
  }

  return <CompetitionInformationSection competiton={data.node} />;
}
