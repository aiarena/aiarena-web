import { getFeatureFlags } from "@/_data/featureFlags";
import Image from "next/image";
import React from "react";
import MainButton from "../_props/MainButton";

interface DiscordInviteCardProps {
  serverName: string;
  inviteUrl: string;
  description: string;
  memberCount: number;
  onlineCount: number;
  serverImageUrl?: string;
}
const DiscordInviteCard: React.FC<DiscordInviteCardProps> = ({
  serverName,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  inviteUrl,
  description,
  memberCount,
  onlineCount,
  serverImageUrl,
}) => {
  const discordData = getFeatureFlags().heroDiscordUsersInfo;

  return (
    <div
      className="shadow-customDiscord bg-customBackgroundColor1 text-white p-6 rounded-lg max-w-[40em] mx-auto  lg:flex lg:justify-center lg:items-center lg:p-10  border border-indigo-500
"
    >
      <div className="flex flex-col md:flex-row items-center gap-8 lg:justify-center">
        {/* Server Image */}
        {serverImageUrl && (
          <div className="flex-shrink-0 w-24 h-24 md:w-32 md:h-32 lg:w-36 lg:h-36">
            <Image
              width={160}
              height={160}
              src={serverImageUrl}
              alt={`${serverName} Server`}
              className="rounded-full w-auto h-auto"
            />
          </div>
        )}

        {/* Card Content */}
        <div className="flex-grow text-center lg:text-center">
          <h2 className="text-3xl font-bold mb-4 text-customGreen font-gugi">
            {serverName}
          </h2>
          <p className="text-gray-400 mb-6 text-sm lg:text-xl lg:mb-8">
            {description}
          </p>
          {discordData ? (
            <div className="flex justify-center gap-6 mb-6">
              <div className="text-green-400">
                <strong>{onlineCount}</strong> Online
              </div>
              <div className="text-gray-300">
                <strong>{memberCount}</strong> Members
              </div>
            </div>
          ) : null}
          <MainButton text=" Join Server" href="inviteUrl" />

          {/* <a
            href={inviteUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="py-3 px-10 w-full md:w-auto inline-block lg:py-4 lg:px-12  hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold rounded-full shadow-lg transition duration-300 ease-in-out transform shadow shadow-black"

          >
            Join Server
          </a> */}
        </div>
      </div>
    </div>
  );
};

export default DiscordInviteCard;

{
  /* <h2 className="text-2xl font-bold mb-2">{serverName}</h2>
          <p className="text-gray-400 mb-4">{description}</p>

          <div className="flex gap-4 mb-6">
            <div className="text-green-400">
              <strong>{onlineCount}</strong> Online
            </div>
            <div className="text-gray-300">
              <strong>{memberCount}</strong> Members
            </div>
          </div> */
}

{
  /* Invite Button */
}

{
  /*              
        {serverImageUrl && (
          <Image
            width={80}
            height={80}
            src={serverImageUrl}
            alt={`${serverName} Server`}
            className="w-full md:w-1/4 rounded-lg mb-4 md:mb-0 md:mr-6"
          />
        )}
     */
}
