"use client";
import EthernetStatusDots from "@/_components/_display/EthernetStatusEffect";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import React, { Suspense, useEffect, useState } from "react";
import mockUptimeData from "@/_data/mockUptime.json";
import PreFooterSpacer from "@/_components/_display/PreFooterSpacer";
import { notFound } from "next/navigation";
import { getFeatureFlags } from "@/_data/featureFlags";
import { graphql, useLazyLoadQuery } from "react-relay";
import { pageStatusQuery } from "./__generated__/pageStatusQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import Link from "next/link";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import LoadingDots from "@/_components/_display/LoadingDots";

const UptimeGraph = ({
  title,
  data,
}: {
  title: string;
  data: { hour: string; uptime: number }[];
}) => {
  return (
    <div className="shadow shadow-black bg-customBackgroundColor1 p-4 rounded-md">
      <WrappedTitle title={title} />
      <div className="h-40 bg-customBackgroundColor1D1  flex items-end justify-between text-gray-300 mb-2 p-2">
        {data.map((entry, index) => (
          <div
            key={index}
            className="w-2 bg-customGreen brightness-75"
            style={{
              height: `${entry.uptime}%`,
              transition: "height 0.3s ease",
            }}
            title={`Hour ${entry.hour}: ${entry.uptime}% uptime`}
          ></div>
        ))}
      </div>
      <EthernetStatusDots />
    </div>
  );
};

const Thanks = ({ user }: { user: { username: string; id: string } }) => {
  return (
    <div className="bg-customBackgroundColor1 mt-8 mb-8 p-4 rounded-md shadow shadow-black ">
      <WrappedTitle title="Thank you" />
      Thank you{" "}
      <Link
        href={`${getPublicPrefix()}/authors/${user.id}`}
        className="text-customGreen"
      >
        {user.username}
      </Link>{" "}
      for supporting AI arena!
    </div>
  );
};

const loadingFallback = () => {
  return (
    <div className="pt-12 pb-24 items-center">
      <p>Loading activity feed...</p>
      <LoadingDots className={"pt-2"} />
    </div>
  );
};

export default function Page() {
  const [isMounted, setIsMounted] = useState(false);
  const data = useLazyLoadQuery<pageStatusQuery>(
    graphql`
      query pageStatusQuery {
        bots(orderBy: "-bot_zip_updated", first: 10) {
          edges {
            node {
              id
              name
              created
              botZipUpdated
              user {
                id
                username
              }
            }
          }
        }
        stats {
          dateTime
          arenaclients
          matchCount1h
          matchCount24h
          randomSupporter {
            id
            username
          }
          buildNumber
        }
      }
    `,
    {}
  );

  const statusPage = getFeatureFlags().statusPage;
  const serverStatus = getFeatureFlags().statusServerStatus;
  const supporters = getFeatureFlags().supporters;

  if (!statusPage) {
    notFound();
    return null;
  }

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return loadingFallback();
  }
  const current_date = new Date(data.stats?.dateTime);

  const formattedDate = current_date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const formattedTime = current_date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

  function createDateString(ms: number) {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    if (hours == 1) {
      return `${hours} hour ago.`;
    }
    if (hours > 0) {
      return `${hours} hours ago.`;
    }
    const minutes = Math.floor(ms / (1000 * 60));
    if (minutes == 1) {
      return `${minutes} minute ago.`;
    }
    if (minutes > 0) {
      return `${minutes} minutes ago.`;
    }
    const seconds = Math.floor(ms / (1000 * 60 * 60));
    if (seconds == 1) {
      return `${seconds} seconds ago.`;
    }
    if (seconds > 0) {
      return `${seconds} seconds ago.`;
    }
  }

  const parsedData = getNodes(data.bots).map((item) => {
    const zip_updated_at = new Date(item.botZipUpdated);

    const item_age = Math.abs(
      zip_updated_at.getTime() - current_date.getTime()
    );
    return {
      bot: {
        name: item.name,
        id: item.id,
      },
      user: item.user,
      age: createDateString(item_age),
    };
  });

  const uptimeData = mockUptimeData;
  return (
    <>
      <div className=" min-h-screen max-w-7xl m-auto pt-8">
        <Suspense fallback={loadingFallback()}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="col-span-1 md:col-span-2">
              {/* <ActivityFeed activities={parsedData} /> */}
              <div className="bg-customBackgroundColor1 p-4 rounded-md shadow shadow-black ">
                <WrappedTitle title="Activity Feed" />
                <ul className="space-y-2">
                  {parsedData.map((activity, index) => (
                    <li
                      key={index}
                      className="text-gray-300 block border-t border-1 border-slate-500"
                    >
                      <div>
                        <p className="pt-2 text-left">
                          Bot{" "}
                          <Link
                            className="font-semibold text-customGreen"
                            href={`${getPublicPrefix()}/bots/${activity.bot.id}`}
                          >
                            {activity.bot.name}
                          </Link>{" "}
                          was updated.
                        </p>
                      </div>
                      <div>
                        <p className="text-left text-slate-500">
                          {activity.age}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div>
              <div className="bg-customBackgroundColor1 p-4 rounded-md shadow shadow-black ">
                <WrappedTitle title="Stats" />
                <ul className="space-y-2 text-gray-300">
                  <li>
                    Date:{" "}
                    <span className="font-semibold text-customGreen">
                      {formattedDate}
                    </span>
                  </li>
                  <li>
                    Time:{" "}
                    <span className="font-semibold text-customGreen">
                      {formattedTime}
                    </span>
                  </li>
                  <li>
                    Matches (1h):{" "}
                    <span className="font-semibold text-customGreen">
                      {data.stats?.matchCount1h}
                    </span>
                  </li>
                  <li>
                    Matches (24h):{" "}
                    <span className="font-semibold text-customGreen">
                      {data.stats?.matchCount24h}
                    </span>
                  </li>
                  <li>
                    Arena Clients:{" "}
                    <span className="font-semibold text-customGreen">
                      {data.stats?.arenaclients}
                    </span>
                  </li>
                  <li>
                    Build:{" "}
                    <span className="font-semibold text-customGreen">
                      {data.stats?.buildNumber}
                    </span>
                  </li>
                </ul>
              </div>
              {supporters &&
              data.stats?.randomSupporter?.username &&
              data.stats?.randomSupporter?.id ? (
                <Thanks user={data.stats?.randomSupporter} />
              ) : null}
            </div>
          </div>
          {serverStatus ? (
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {uptimeData.map((server) => (
                <UptimeGraph
                  key={server.serverName}
                  title={server.serverName}
                  data={server.data}
                />
              ))}
            </div>
          ) : null}
        </Suspense>
      </div>
      <PreFooterSpacer />
    </>
  );
}
