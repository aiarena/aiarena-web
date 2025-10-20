import { graphql, useFragment } from "react-relay";
import { ResultsSection_node$key } from "./__generated__/ResultsSection_node.graphql";
import ResultsTable from "./ResultsTable";

interface ResultsSectionProps {
  data: ResultsSection_node$key;
}

export default function ResultsSection(props: ResultsSectionProps) {
  const data = useFragment(
    graphql`
      fragment ResultsSection_node on Query {
        ...ResultsTable_node
      }
    `,
    props.data,
  );

  return (
    <section className="h-full" aria-labelledby="results-heading">
      <h2 id="results-heading" className="sr-only">
        Results
      </h2>

      <div role="region" aria-labelledby="results-table-heading">
        <h3 id="results-table-heading" className="sr-only">
          Results Table
        </h3>
        <ResultsTable data={data} />
      </div>
    </section>
  );
}
