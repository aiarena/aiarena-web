import React from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import WrappedTitle from "./WrappedTitle";
import clsx from "clsx";
import { LegacyActivityListQuery } from "./__generated__/LegacyActivityListQuery.graphql";
import FetchError from "./FetchError";
import { Link } from "react-router";
import timeAgoShort from "@/_lib/timeAgoSort";

const LegacyActivityList: React.FC = () => {
  const data = useLazyLoadQuery<LegacyActivityListQuery>(
    graphql`
      query LegacyActivityListQuery {
        bots(orderBy: "botZipUpdated", last: 15) {
          edges {
            node {
              id
              user {
                id
                username
              }
              name
              botZipUpdated
              created
            }
          }
        }
      }
    `,
    {},
  );
  if (!data.bots) {
    return <FetchError type="bots" />;
  }

  function createEventText({
    botName,
    botId,
    botAuthorName,
    botAuthorId,
    botUpdatedAt,
    botUploadedAt,
  }: {
    botName: string;
    botId: string;
    botAuthorName: string;
    botAuthorId: string;
    botUpdatedAt: string;
    botUploadedAt: string;
  }) {
    const updatedAt = new Date(botUpdatedAt).getTime();
    const uploadedAt = new Date(botUploadedAt).getTime();

    const diffSeconds = Math.abs(updatedAt - uploadedAt) / 1000;
    const isUpdate = diffSeconds > 1; // > 1 sec → update, else create, same as old backend

    return isUpdate ? (
      <>
        Bot{" "}
        <a
          href={`/bots/${getIDFromBase64(botId, "BotType")}`}
          aria-label={`View bot profile for ${botName}`}
        >
          {botName}
        </a>{" "}
        was updated.
      </>
    ) : (
      <>
        <Link
          to={`/authors/${getIDFromBase64(botAuthorId, "UserType")}`}
          aria-label={`View user profile for ${botAuthorName}`}
        >
          {botAuthorName}
        </Link>{" "}
        uploaded a new bot:{" "}
        <a
          href={`/bots/${getIDFromBase64(botId, "BotType")}`}
          aria-label={`View bot profile for ${botName}`}
        >
          {botName}
        </a>
      </>
    );
  }

  return (
    <div>
      <WrappedTitle title="Activity" font="font-bold" />
      <table className="w-full text-sm">
        <thead className="bg-customGreen-dark-2 h-9 ">
          <tr>
            <th className="min-w-[6em]">Time</th>
            <th>Event</th>
          </tr>
        </thead>
        <tbody>
          {getNodes(data.bots)
            .reverse()
            .map((bot, idx) => (
              <tr
                key={bot.id}
                className={clsx(" h-12", idx % 2 ? "bg-darken-4" : "bg-darken")}
              >
                <td className="text-center pr-4">
                  {timeAgoShort(bot.botZipUpdated)} ago
                </td>

                <td>
                  {createEventText({
                    botName: bot.name,
                    botId: bot.id,
                    botAuthorName: bot.user.username,
                    botAuthorId: bot.user.id,
                    botUpdatedAt: bot.botZipUpdated,
                    botUploadedAt: bot.created,
                  })}
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default LegacyActivityList;
