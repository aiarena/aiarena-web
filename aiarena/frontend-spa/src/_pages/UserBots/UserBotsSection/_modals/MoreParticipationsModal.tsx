import { Suspense } from "react";
import { CheckCircleIcon } from "@heroicons/react/24/solid";
import { graphql, useFragment, useLazyLoadQuery } from "react-relay";

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
      }
    `,
    props.viewer,
  );

  const discordBonus = viewer.activeBotParticipationDiscordBonus;

  return (
    <Modal
      onClose={props.onClose}
      isOpen={props.isOpen}
      title="Get more active participations"
    >
      <div className="mb-6">
        {discordBonus > 0 ? (
          <>
            {viewer.linkedDiscord ? (
              <div className="flex items-center gap-3 border border-customGreen bg-customGreen/10 px-3 py-2 text-white">
                <DiscordIcon linked />
                <span className="grow">Discord linked</span>
                <span className="text-lg font-bold text-customGreen">
                  +{discordBonus}
                </span>
              </div>
            ) : (
              <a
                href={reverseUrl("discord_bind_index")}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 border border-customGreen/50 bg-darken-4 px-3 py-2 text-white hover:bg-darken-6"
              >
                <DiscordIcon linked={false} />
                <span className="grow">Link Discord</span>
                <span className="text-lg font-bold text-customGreen">
                  +{discordBonus}
                </span>
              </a>
            )}

            <SectionDivider color="gray" className="my-4 pb-1" />
          </>
        ) : null}

        <h3 className="mb-2 font-semibold">Support on Patreon</h3>

        {/* Only fetch the tiers once the modal is actually opened. */}
        {props.isOpen ? (
          <Suspense
            fallback={
              <div className="flex justify-center py-6">
                <LoadingSpinner color="light-gray" />
              </div>
            }
          >
            <SupporterTiers />
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

function SupporterTiers() {
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
      {data.supporterTiers.map((tier) => {
        const isFree = tier.level === "none";
        return (
          <li key={tier.level} className="flex items-center gap-3 px-3 py-2">
            {isFree ? (
              <span className="h-6 w-6" />
            ) : (
              <img
                src={`${getPublicPrefix()}/bot-icons/${tier.level}.png`}
                alt=""
                className="h-6 w-6"
              />
            )}
            <span className="grow">{isFree ? "Free" : tier.name}</span>
            <span className="text-lg font-bold tabular-nums text-white">
              {tier.activeBotParticipationLimit.toLocaleString()}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

function DiscordIcon({ linked }: { linked: boolean }) {
  return (
    <span className="relative h-6 w-6 shrink-0">
      <img
        src={`${getPublicPrefix()}/social_icons/discord-icon.svg`}
        alt=""
        className="h-6 w-6"
      />
      {linked ? (
        <CheckCircleIcon
          aria-label="Linked"
          className="absolute -right-1.5 -bottom-1.5 h-4 w-4 rounded-full bg-neutral-900 text-customGreen"
        />
      ) : null}
    </span>
  );
}
