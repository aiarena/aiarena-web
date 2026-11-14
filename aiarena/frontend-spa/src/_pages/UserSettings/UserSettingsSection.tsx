import { graphql, useFragment } from "react-relay";

import { getDateToLocale } from "@/_lib/dateUtils";
import { UserSettingsSection_viewer$key } from "./__generated__/UserSettingsSection_viewer.graphql";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";
import SectionDivider from "@/_components/_display/SectionDivider";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";
import TokenReveal from "@/_components/_actions/TokenReveal";
import RegenerateTokenButton from "@/_components/_actions/RegenerateTokenButton";
import SquareButton from "@/_components/_actions/SquareButton";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountSettingsCard from "./_components/AccountSettingsCard";
import SettingsCard from "./_components/SettingsCard";
import SettingsToggleRow from "./_components/SettingsToggleRow";
import SettingsGroup from "./_components/SettingsGroup";

interface UserSettingsSectionProps {
  viewer: UserSettingsSection_viewer$key;
}

export default function UserSettingsSection(props: UserSettingsSectionProps) {
  const viewer = useFragment(
    graphql`
      fragment UserSettingsSection_viewer on Viewer {
        ...TokenReveal_viewer
        ...RegenerateTokenButton_viewer
        ...AccountSettingsCard_viewer
        lastLogin
        dateJoined
        firstName
        lastName
        user {
          username
          patreonLevel
          ...AvatarWithBorder_user
        }
      }
    `,
    props.viewer,
  );

  const [hideSpoilers, setHideSpoilers] = useStateWithLocalStorage<boolean>(
    "Profile_Hide_Spoilers",
    false,
  );

  const StatusInfo = () => {
    return (
      <dl
        className="ml-4 text-sm text-gray-300 space-y-2"
        role="list"
        aria-label="Account information"
      >
        <div className="flex" role="listitem">
          <dt className="w-36 font-medium text-white">Date Joined:</dt>
          <dd>{getDateToLocale(viewer.dateJoined)}</dd>
        </div>
        <div className="flex" role="listitem">
          <dt className="w-36 font-medium text-white">Last Login:</dt>
          <dd>{getDateToLocale(viewer.lastLogin)}</dd>
        </div>
      </dl>
    );
  };

  return (
    <section className="" aria-labelledby="user-settings-heading">
      <h2 id="user-settings-heading" className="sr-only">
        User Settings and Profile
      </h2>
      {/* sidesection */}
      <div className="lg:flex lg:flex-row lg:gap-4">
        <div className="relative m-0 md:m-3 lg:shrink-0">
          <div className="flex justify-center">
            {viewer?.user ? (
              <AvatarWithBorder user={viewer.user} size="xl" />
            ) : null}
          </div>
          {/* desktop view statusinfo */}
          <div className="hidden lg:block mt-4">
            <StatusInfo />
          </div>
          <div className="hidden lg:block mt-4"></div>
        </div>

        {/* mainsection: takes the space left beside the avatar column (min-w-0
            lets it shrink; w-full would be the whole row and overflow it) */}
        <div className="min-w-0 lg:flex-1">
          <div className="lg:block lg:text-left flex justify-center">
            <div className="leading-tight py-4">
              <h4
                className="font-bold text-2xl lg:block lg:text-left flex justify-center pb-4"
                id="author-name"
              >
                {viewer?.user?.username}
              </h4>
              {viewer.firstName || viewer.lastName ? (
                <p className="  lg:block lg:text-left flex justify-center">
                  {viewer.firstName} {viewer.lastName}
                </p>
              ) : null}
              {viewer?.user?.patreonLevel &&
              viewer.user.patreonLevel != "NONE" ? (
                <p className="font-thin lg:block lg:text-left flex justify-center pb-4">
                  <i>Supporter</i>
                </p>
              ) : null}
              {/* mobile view statusinfo */}
              <div className="block lg:hidden pt-4">
                <StatusInfo />
              </div>
            </div>
          </div>
          <SectionDivider className="pb-4" />
          {/* Masonry-style columns: cards differ a lot in height, so a grid would
              leave gaps beside the tall Account card; columns pack them. The
              breakpoints are late because the dashboard nav and the avatar
              column already take ~450px of the viewport. */}
          <div className="columns-1 xl:columns-2 2xl:columns-3 gap-6 [&>*]:mb-6 [&>*]:break-inside-avoid">
            <AccountSettingsCard viewer={viewer} />

            <SettingsCard title="API Token">
              <SettingsGroup title="Your token">
                <TokenReveal viewer={viewer} />
                <RegenerateTokenButton viewer={viewer} outerClassName="self-start" />
              </SettingsGroup>

              <SettingsGroup title="GraphQL API">
                <p className="text-sm text-gray-300">
                  For deeper queries, fewer requests, and an interactive
                  playground, check out our new GraphQL API.
                </p>
                <SquareButton
                  href={reverseUrl("developers")}
                  text="API docs →"
                  outerClassName="self-start"
                />
              </SettingsGroup>
            </SettingsCard>

            <SettingsCard title="Website settings">
              <SettingsGroup title="Display">
                <SettingsToggleRow
                  label="Hide spoilers"
                  enabled={hideSpoilers ?? false}
                  onChange={setHideSpoilers}
                />
              </SettingsGroup>
            </SettingsCard>
          </div>
        </div>
      </div>
    </section>
  );
}
