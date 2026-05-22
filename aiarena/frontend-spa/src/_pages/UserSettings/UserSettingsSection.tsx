import { graphql, useFragment, useMutation } from "react-relay";

import { getDateToLocale } from "@/_lib/dateUtils";
import { UserSettingsSection_viewer$key } from "./__generated__/UserSettingsSection_viewer.graphql";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";
import SectionDivider from "@/_components/_display/SectionDivider";
import SocialLinkCard from "@/_components/_display/SocialLinkCard";
import { footerLinks } from "@/_data/footerLinks";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import { UserSettingsSectionLogoutMutation } from "./__generated__/UserSettingsSectionLogoutMutation.graphql";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import useStateWithLocalStorage from "@/_components/_hooks/useStateWithLocalStorage";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import TokenReveal from "@/_components/_actions/TokenReveal";
import SquareButton from "@/_components/_actions/SquareButton";
interface UserSettingsSectionProps {
  viewer: UserSettingsSection_viewer$key;
}

export default function UserSettingsSection(props: UserSettingsSectionProps) {
  const viewer = useFragment(
    graphql`
      fragment UserSettingsSection_viewer on Viewer {
        apiToken
        receiveEmailComms
        lastLogin
        dateJoined
        firstName
        lastName
        linkedDiscord
        linkedPatreon
        user {
          username
          patreonLevel
          ...AvatarWithBorder_user
        }
      }
    `,
    props.viewer,
  );

  const [logout, updating] = useMutation<UserSettingsSectionLogoutMutation>(
    graphql`
      mutation UserSettingsSectionLogoutMutation {
        signOut {
          errors {
            messages
            field
          }
        }
      }
    `,
  );
  const [hideSpoilers, setHideSpoilers] = useStateWithLocalStorage<boolean>(
    "Profile_Hide_Spoilers",
    false,
  );

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "signOut",
    "Successfully logged out! Redirecting...",
  );

  const handleLogout = () => {
    logout({
      variables: {},
      onCompleted: (...args) => {
        const success = onCompleted(...args);
        if (success) {
          window.location.href = "/";
        }
      },
      onError,
    });
  };

  const handleLinkDiscord = () => {
    window.open("/discord/", "_blank", "noopener,noreferrer");
  };
  const handleUnlinkDiscord = () => {
    window.open("/profile/unlink/discord/", "_blank", "noopener,noreferrer");
  };

  const handleLinkPatreon = () => {
    window.open("/patreon/", "_blank", "noopener,noreferrer");
  };

  const handleUnlinkPatreon = () => {
    window.open("/profile/unlink/patreon/", "_blank", "noopener,noreferrer");
  };

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
        <div className="flex" role="listitem">
          <dt className="w-36 font-medium text-white">Receive Emails:</dt>
          <dd>{viewer.receiveEmailComms ? "Yes" : "No"}</dd>
        </div>
        <div className="grid gap-4">
          <a id="change_password" href="/accounts/password_change/">
            Change password
          </a>
          <button
            onClick={handleLogout}
            className="text-white bg-red-500 px-2 py-0.5 rounded hover:bg-red-400 w-24 flex justify-around"
          >
            {!updating ? <p>Logout</p> : <LoadingSpinner color="white" />}
          </button>
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
        <div className="relative m-0 md:m-3">
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

        {/* mainsection */}
        <div className="w-full">
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
          <div className="gap-4 flex flex-col max-w-[26em]">
            <SocialLinkCard
              title="Discord"
              iconPath={
                footerLinks.socialLinks.find((it) => it.name == "Discord")?.icon
              }
            >
              {viewer.linkedDiscord ? (
                <button
                  onClick={handleUnlinkDiscord}
                  className="text-white bg-red-500 px-2 py-0.5 rounded hover:bg-red-400"
                >
                  Unlink
                </button>
              ) : (
                <button
                  onClick={handleLinkDiscord}
                  className="text-white bg-indigo-500 px-2 py-0.5 rounded hover:bg-indigo-400"
                >
                  Link
                </button>
              )}
            </SocialLinkCard>
            <SocialLinkCard
              title="Patreon"
              iconPath={
                footerLinks.socialLinks.find((it) => it.name == "Patreon")?.icon
              }
              invert
            >
              {viewer.linkedPatreon ? (
                <button
                  onClick={handleUnlinkPatreon}
                  className="text-white bg-red-500 px-2 py-0.5 rounded hover:bg-red-400"
                >
                  Unlink
                </button>
              ) : (
                <button
                  onClick={handleLinkPatreon}
                  className="text-white bg-indigo-500 px-2 py-0.5 rounded hover:bg-indigo-400"
                >
                  Link
                </button>
              )}
            </SocialLinkCard>

            {/* API Token */}
            <div className="bg-darken-2 border border-neutral-600 shadow-lg shadow-black rounded-md backdrop-blur-sm">
              <h3 className="mt-1 ml-2 text-base font-semibold ">API Token</h3>
              <div className=" p-4">
                <TokenReveal token={viewer.apiToken} />

                <p className="text-sm text-gray-300 mt-3">
                  For deeper queries, fewer requests, and an interactive
                  playground, check out our new GraphQL API.
                </p>

                <SquareButton
                  href="/developers/"
                  text="API docs →"
                  outerClassName="mt-2"
                />
              </div>
            </div>

            {/* Website settings */}
            <div className="bg-darken-2 border border-neutral-600 shadow-lg shadow-black rounded-md backdrop-blur-sm">
              <h3 className="mt-1 ml-2 text-base font-semibold">Website settings</h3>

              <div className="p-4">
                <div className="flex items-center justify-between gap-4 bg-black text-gray-300 px-2 py-2 rounded text-sm">
                  <span>Hide spoilers</span>

                  <SimpleToggle
                    enabled={hideSpoilers ?? false}
                    onChange={setHideSpoilers}
                  />

                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}
