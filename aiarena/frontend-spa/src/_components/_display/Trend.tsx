import { graphql, useFragment } from "react-relay";
import clsx from "clsx";
import { Trend_competitionParticipation$key } from "./__generated__/Trend_competitionParticipation.graphql";

interface TrendProps {
  competitionParticipation: Trend_competitionParticipation$key;
}

export default function Trend(props: TrendProps) {
  const competitionParticipation = useFragment(
    graphql`
      fragment Trend_competitionParticipation on CompetitionParticipationType {
        trend
      }
    `,
    props.competitionParticipation
  );

  return (
    <div>
      {" "}
      Trend:{" "}
      {
        <span
          className={clsx(
            "font-normal",
            (competitionParticipation.trend ?? 0) > 0 && "text-customGreen",
            (competitionParticipation.trend ?? 0) === 0 && "text-gray-300",
            (competitionParticipation.trend ?? 0) < 0 && "text-red-500"
          )}
        >
          {competitionParticipation.trend ?? 0}
        </span>
      }
    </div>
  );
}
