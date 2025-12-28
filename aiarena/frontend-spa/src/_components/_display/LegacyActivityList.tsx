import React from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import WrappedTitle from "./WrappedTitle";
import clsx from "clsx";
import { LegacyActivityListQuery } from "./__generated__/LegacyActivityListQuery.graphql";
import FetchError from "./FetchError";

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
    {}
  );
  if (!data.bots) {
    return <FetchError type="bots" />;
  }
  function timeAgoShort(
    from: Date | number | string,
    to: Date | number = Date.now()
  ): string {
    const start = new Date(from).getTime();
    const end = new Date(to).getTime();
    let ms = Math.abs(end - start);

    const MS = {
      w: 7 * 24 * 60 * 60 * 1000,
      d: 24 * 60 * 60 * 1000,
      h: 60 * 60 * 1000,
      m: 60 * 1000,
      s: 1000,
    };

    const parts: Array<[number, string]> = [];

    const w = Math.floor(ms / MS.w);
    if (w) parts.push([w, "w"]);
    ms %= MS.w;
    const d = Math.floor(ms / MS.d);
    if (d) parts.push([d, "d"]);
    ms %= MS.d;
    const h = Math.floor(ms / MS.h);
    if (h) parts.push([h, "h"]);
    ms %= MS.h;
    const m = Math.floor(ms / MS.m);
    if (m) parts.push([m, "m"]);
    ms %= MS.m;
    const s = Math.floor(ms / MS.s);
    if (s) parts.push([s, "s"]);

    if (parts.length === 0) return "0s";

    if (parts[0][1] === "w") {
      // Only return the week if the string starts with a week count
      return parts
        .slice(0, 1)
        .map(([v, u]) => `${v}${u}`)
        .join(" ");
    }

    // else return two largest units - i.e. day, hour /or/ hour, minute
    return parts
      .slice(0, 2)
      .map(([v, u]) => `${v}${u}`)
      .join(" ");
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
        <a
          href={`/users/${getIDFromBase64(botAuthorId, "UserType")}`}
          aria-label={`View user profile for ${botAuthorName}`}
        >
          {botAuthorName}
        </a>{" "}
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
