import { useState } from "react";
import { graphql, useFragment } from "react-relay";

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
        user {
          username
          patreonLevel

          ...AvatarWithBorder_user
        }
      }
    `,
    props.viewer
  );
  const { enqueueSnackbar } = useSnackbar();
  const [apiTokenVisible, setApiTokenVisible] = useState(false);

  // const [discordLinked, setDiscordLinked] = useState(false);
  // const [patreonLinked, setPatreonLinked] = useState(false);

  // const handleLinkDiscord = () => setDiscordLinked(true);
  // const handleUnlinkDiscord = () => setDiscordLinked(false);
  // const handleLinkPatreon = () => setPatreonLinked(true);
  // const handleUnlinkPatreon = () => setPatreonLinked(false);

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
            {/* <div className="bg-gray-700 p-4 rounded-md ">
              <h3 className="text-base font-semibold text-customGreen">
                Connected Accounts
              </h3>
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center space-x-2">
                  <svg
                    className="w-4 h-4 text-indigo-400"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M20.317 4.369A19.791 19.791 0 0016.845 3c-.247.454-.53 1.047-.721 1.514a17.835 17.835 0 00-4.248 0c-.191-.467-.474-1.06-.721-1.514A19.781 19.781 0 003.683 4.37C.976 9.05 0 13.5 0 17.752c0 0 4.144 3.697 8.298 3.697h.878a7.548 7.548 0 007.547-7.547c0-.056 0-.11-.002-.165 1.102-.794 2.03-1.695 2.805-2.7a19.248 19.248 0 001.79-2.6z" />
                  </svg>
                  <span className="text-gray-300">Discord:</span>
                  {discordLinked ? (
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
                </div>

                <div className="flex items-center space-x-2">
                  <svg
                    className="w-4 h-4 text-red-400"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <circle cx="12" cy="12" r="9" />
                  </svg>
                  <span className="text-gray-300">Patreon:</span>
                  {patreonLinked ? (
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
                </div>
              </div>
            </div> */}

            {/* API Token */}
            <div className="bg-darken-2 border border-neutral-600 shadow-lg shadow-black rounded-md backdrop-blur-sm">
              <h3 className="mt-1 ml-2 text-base font-semibold text-customGreen">
                API Token
              </h3>
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
