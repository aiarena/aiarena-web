import { graphql, useLazyLoadQuery } from "react-relay";
import { ResultsQuery } from "./__generated__/ResultsQuery.graphql";
import ResultsSection from "./ResultsSection";

export default function Results() {
  const data = useLazyLoadQuery<ResultsQuery>(
    graphql`
      query ResultsQuery {
        ...ResultsSection_node
      }
    `,
    {},
  );

  return (
    <>
      <ResultsSection data={data} />
    </>
  );
}
