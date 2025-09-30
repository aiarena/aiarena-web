import { graphql, useFragment } from "react-relay";
import { ResultsSection_node$key } from "./__generated__/ResultsSection_node.graphql";
import ResultsTable from "./ResultsTable";

interface UserMatchRequestsSectionProps {
  data: ResultsSection_node$key;
}

export default function ResultsSection(props: UserMatchRequestsSectionProps) {
  const data = useFragment(
    graphql`
      fragment ResultsSection_node on Query {
        ...ResultsTable_node
      }
    `,
    props.data
  );

  return (
    <section className="h-full" aria-labelledby="match-requests-heading">
      <h2 id="match-requests-heading" className="sr-only">
        Match Requests
      </h2>

      <div role="region" aria-labelledby="match-requests-table-heading">
        <h3 id="match-requests-table-heading" className="sr-only">
          Match Requests Table
        </h3>
        <ResultsTable data={data} />
      </div>
    </section>
  );
}
