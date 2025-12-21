import { useState } from "react";
import { graphql, useFragment, useMutation } from "react-relay";

import { getDateToLocale } from "@/_lib/dateUtils";
import {
  ClipboardDocumentIcon,
  EyeIcon,
  EyeSlashIcon,
} from "@heroicons/react/20/solid";
import { useSnackbar } from "notistack";
import { UserSettingsSection_viewer$key } from "./__generated__/UserSettingsSection_viewer.graphql";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";
import SectionDivider from "@/_components/_display/SectionDivider";
import SocialLinkCard from "@/_components/_display/SocialLinkCard";
import { footerLinks } from "@/_data/footerLinks";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import { UserSettingsSectionLogoutMutation } from "./__generated__/UserSettingsSectionLogoutMutation.graphql";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
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
    props.viewer
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
    `
  );

  const { enqueueSnackbar } = useSnackbar();
  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "signOut",
    "Successfully logged out! Redirecting..."
  );
  const [apiTokenVisible, setApiTokenVisible] = useState(false);

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

  const handleCopyToken = () => {
    navigator.clipboard.writeText(viewer.apiToken ?? "");
    enqueueSnackbar("API token copied to clipboard!");
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
                <div className="flex items-center gap-2 bg-black text-gray-300 px-2 py-1 rounded font-mono text-xs break-words ">
                  <span className="flex-1 truncate">
                    {apiTokenVisible
                      ? viewer.apiToken
                      : "•••••••••••••••••••••••••••••••••••••••"}
                  </span>

                  <button
                    onClick={() => setApiTokenVisible(!apiTokenVisible)}
                    className="text-white  hover:text-gray-400 p-1"
                    title={apiTokenVisible ? "Hide token" : "Show token"}
                  >
                    {apiTokenVisible ? (
                      <EyeSlashIcon className="h-4 w-4" />
                    ) : (
                      <EyeIcon className="h-4 w-4" />
                    )}
                  </button>

                  <button
                    onClick={handleCopyToken}
                    className="text-white hover:text-gray-400 p-1"
                    title="Copy token"
                  >
                    <ClipboardDocumentIcon className="h-4 w-4" />
                  </button>
                </div>

                <div className="flex gap-4 mt-2 text-sm">
                  <a href="/wiki/data-api/" target="_blank">
                    Wiki
                  </a>
                  <a href="/api/" target="_blank">
                    API Endpoints
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
