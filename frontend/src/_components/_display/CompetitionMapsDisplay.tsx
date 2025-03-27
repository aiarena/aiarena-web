import React from "react";
import { graphql, useFragment } from "react-relay";
import { CompetitionMapsDisplay_competition$key } from "./__generated__/CompetitionMapsDisplay_competition.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import MapDisplay from "./MapDisplay";

interface CompetitionMapsDisplayProps {
  competition: CompetitionMapsDisplay_competition$key;
}

export default function CompetitionMapsDisplay(
  props: CompetitionMapsDisplayProps
) {
  const competition = useFragment(
    graphql`
      fragment CompetitionMapsDisplay_competition on CompetitionType {
        maps {
          edges {
            node {
              id
              name
              downloadLink
            }
          }
        }
      }
    `,
    props.competition
  );

  const maps = getNodes(competition.maps);

  return (
    <div>
      <h3 className=" text-2xl font-semibold text-customGreen my-4">Maps</h3>
      <div className="flex flex-wrap justify-center gap-4">
        {maps &&
          maps.map((map) => (
            <div key={map.id} className="flex-none w-28 h-32">
              <MapDisplay
                mapName={map.name}
                imageUrl={`/maps/${map.name}.webp`}
                downloadLink={map.downloadLink}
              />
            </div>
          ))}
      </div>
    </div>
  );
}
