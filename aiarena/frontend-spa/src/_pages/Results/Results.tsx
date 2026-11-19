import { graphql, useLazyLoadQuery } from "react-relay";
import { ResultsQuery } from "./__generated__/ResultsQuery.graphql";
import ResultsSection from "./ResultsSection";
import FetchError from "@/_components/_display/FetchError";

export default function Results() {
  const data = useLazyLoadQuery<ResultsQuery>(
    graphql`
      query ResultsQuery {
        ...ResultsSection_node
      }
    `,
    {}
  );
  if (!data) {
    return <FetchError type="results" />;
  }

  return (
    <>
      <ResultsSection data={data} />
    </>
  );
}
