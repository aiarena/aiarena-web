import { Suspense } from "react";
import { graphql, useFragment, useLazyLoadQuery } from "react-relay";
import clsx from "clsx";

import Modal from "@/_components/_actions/Modal";
import SquareButton from "@/_components/_actions/SquareButton";
import SectionDivider from "@/_components/_display/SectionDivider";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { socialLinks } from "@/_data/socialLinks";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { reverseUrl } from "@/_lib/reverseUrl";
import { MoreParticipationsModal_viewer$key } from "./__generated__/MoreParticipationsModal_viewer.graphql";
import { MoreParticipationsModalTiersQuery } from "./__generated__/MoreParticipationsModalTiersQuery.graphql";

interface MoreParticipationsModalProps {
  viewer: MoreParticipationsModal_viewer$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function MoreParticipationsModal(
  props: MoreParticipationsModalProps,
) {
  const viewer = useFragment(
    graphql`
      fragment MoreParticipationsModal_viewer on Viewer {
        linkedDiscord
        activeBotParticipationDiscordBonus
        user {
          patreonLevel
        }
      }
    `,
    props.viewer,
  );

  const discordBonus = viewer.activeBotParticipationDiscordBonus;
  const showDiscordBonus = !viewer.linkedDiscord && discordBonus > 0;

  return (
    <Modal
      onClose={props.onClose}
      isOpen={props.isOpen}
      title="Get more active participations"
    >
      <div className="mb-6">
        {showDiscordBonus ? (
          <>
            <a
              href={reverseUrl("discord_bind_index")}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 border border-customGreen/50 bg-darken-4 px-3 py-2 text-white hover:bg-darken-6"
            >
              <img
                src={`${getPublicPrefix()}/social_icons/discord-icon.svg`}
                alt=""
                className="h-6 w-6"
              />
              <span className="grow">Link Discord</span>
              <span className="text-lg font-bold text-customGreen">
                +{discordBonus}
              </span>
            </a>

            <SectionDivider color="gray" className="my-4 pb-1" />
          </>
        ) : null}

        <h3 className="mb-2 font-semibold">Support us on Patreon</h3>

        {/* Only fetch the tiers once the modal is actually opened. */}
        {props.isOpen ? (
          <Suspense
            fallback={
              <div className="flex justify-center py-6">
                <LoadingSpinner color="light-gray" />
              </div>
            }
          >
            <SupporterTiers
              currentLevel={viewer.user?.patreonLevel?.toLowerCase() ?? null}
            />
          </Suspense>
        ) : null}

        <SquareButton
          text="Support on Patreon"
          onClick={() =>
            window.open(socialLinks["patreon"], "_blank", "noopener,noreferrer")
          }
          outerClassName="w-full mt-4"
        />
      </div>
    </Modal>
  );
}

function SupporterTiers({ currentLevel }: { currentLevel: string | null }) {
  const data = useLazyLoadQuery<MoreParticipationsModalTiersQuery>(
    graphql`
      query MoreParticipationsModalTiersQuery {
        supporterTiers {
          level
          name
          activeBotParticipationLimit
        }
      }
    `,
    {},
  );

  return (
    <ul className="flex flex-col">
      {data.supporterTiers
        .filter((tier) => tier.level !== "none")
        .map((tier) => (
          <li
            key={tier.level}
            className={clsx(
              "flex items-center gap-3 border px-3 py-2",
              tier.level === currentLevel
                ? "border-customGreen/50 bg-customGreen/10"
                : "border-transparent",
            )}
          >
            <img
              src={`${getPublicPrefix()}/bot-icons/${tier.level}.png`}
              alt=""
              className="h-6 w-6"
            />
            <span className="grow">
              {tier.name}
              {tier.level === currentLevel ? (
                <span className="ml-2 text-xs text-gray-400">current</span>
              ) : null}
            </span>
            <span className="text-lg font-bold tabular-nums text-white">
              {tier.activeBotParticipationLimit.toLocaleString()}
            </span>
          </li>
        ))}
    </ul>
  );
}

