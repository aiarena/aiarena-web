import { getBase64FromID } from "@/_lib/relayHelpers";
import { useLazyLoadQuery } from "react-relay";
import { useParams } from "react-router";
import { graphql } from "relay-runtime";
import AuthorProfile from "./AuthorProfile";
import { AuthorSectionQuery } from "./__generated__/AuthorSectionQuery.graphql";
import AuthorBotsTable from "./AuthorBots";

export default function AuthorSection() {
  const { userId: authorId } = useParams<{ userId: string }>();
  const data = useLazyLoadQuery<AuthorSectionQuery>(
    graphql`
      query AuthorSectionQuery($id: ID!) {
        node(id: $id) {
          ... on UserType {
            ...AuthorProfile_user
            ...AuthorBotsTable_user
          }
        }
      }
    `,
    { id: getBase64FromID(authorId!, "UserType") || "" }
  );

  if (!data.node) return <div>Author not found</div>;

  return (
    <>
      <div className="max-w-7xl mx-auto">
        <AuthorProfile author={data.node} />
        <AuthorBotsTable data={data.node} />
      </div>
    </>
  );
}
