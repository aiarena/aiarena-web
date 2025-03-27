import Image from "next/image";
import { graphql, useFragment } from "react-relay";
import { CompetitionHeader_competition$key } from "./__generated__/CompetitionHeader_competition.graphql";

interface CompetitionHeaderProps {
  competition: CompetitionHeader_competition$key;
}

export default function CompetitionHeader(props: CompetitionHeaderProps) {
  const competition = useFragment(
    graphql`
      fragment CompetitionHeader_competition on CompetitionType {
        name
        status
      }
    `,
    props.competition
  );

  return (
    <div className="relative w-full h-36 md:h-36 lg:h-36">
      <Image
        src={"/competitions/sc2_1.webp"}
        alt={`${competition.name} banner`}
        layout="fill"
        objectFit="cover"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="text-center text-white px-4">
          <h1 className="text-3xl md:text-5xl font-bold">{competition.name}</h1>
          <p className="text-lg md:text-2xl mt-2">
            <b>Status: </b>
            {competition.status}
          </p>
        </div>
      </div>
    </div>
  );
}
