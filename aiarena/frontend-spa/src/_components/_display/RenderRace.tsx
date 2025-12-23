import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { CoreBotRaceLabelChoices } from "@/_pages/Rework/Bots/__generated__/BotsTable_node.graphql";
import { ReactNode } from "react";
import clsx from "clsx";

export function RenderRace({
  race,
}: {
  race:
    | {
        label: CoreBotRaceLabelChoices;
        name: string | null | undefined;
      }
    | undefined;
}): ReactNode | string {
  const races = {
    P: {
      image: `${getPublicPrefix()}/sc2-race/protoss.svg`,
      appendStyle: undefined,
    },
    R: {
      image: `${getPublicPrefix()}/sc2-race/random.svg`,
      appendStyle: "scale-90",
    },
    T: {
      image: `${getPublicPrefix()}/sc2-race/terran.svg`,
      appendStyle: undefined,
    },
    Z: {
      image: `${getPublicPrefix()}/sc2-race/zerg.svg`,
      appendStyle: undefined,
    },
  };

  if (race && race.label in races) {
    return (
      <span className="flex ">
        <img
          src={races[race.label].image}
          alt={race.name + "-Icon"}
          title={race.name || ""}
          className={clsx(
            "mr-2 h-[25px] w-[25px]",
            races[race.label].appendStyle
          )}
        />
        <p>{race.name}</p>
      </span>
    );
  } else {
    return <span>{race?.name || ""}</span>;
  }
}
