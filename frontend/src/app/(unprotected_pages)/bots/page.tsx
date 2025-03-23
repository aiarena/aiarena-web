"use client";
import FilterableList from "@/_components/_display/FilterableList";
import { formatDate } from "@/_lib/dateUtils";
import Link from "next/link";
import { getFeatureFlags } from "@/_data/featureFlags";
import { notFound } from "next/navigation";
import { useBots } from "@/_components/_hooks/useBots";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { graphql, useLazyLoadQuery } from "react-relay";
import { pageBotsQuery } from "./__generated__/pageBotsQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";

export default function Page() {
  const botsPage = getFeatureFlags().botsPage;

  const data = useLazyLoadQuery<pageBotsQuery>(
    graphql`
      query pageBotsQuery {
        bots {
          edges {
            node {
              id
              name
              created
              type
              user {
                id
                username
              }
            }
          }
        }
      }
    `,
    {}
  );

  if (!botsPage) {
    notFound();
  }
  if (!data.bots) {
    notFound();
  }

  return (
    <>
      <FilterableList
        data={getNodes(data.bots)}
        fields={["name", "created", "type", "user.username"]} // Pass nested field as string
        fieldLabels={{
          name: "Bot Name",
          created: "Date Created",
          "user.username": "Author",
          type: "Type",
        }}
        fieldClasses={{
          "user.username": "hidden md:block",
          type: "hidden sm:block",
        }}
        filters={[
          {
            type: "search",
            label: "Search",
            field: "all",
            placeholder: "Search all fields...",
          },
          {
            type: "dropdown",
            label: "Type",
            field: "type",
            placeholder: "Select type",
          },
        ]}
        renderRow={(item) => (
          <div className="block p-4 hover:bg-gray-800 rounded transition flex justify-between items-center shadow-md border border-gray-700">
            <div className="grid grid-cols-[repeat(auto-fit,_minmax(0,_1fr))]  w-full">
              <Link
                href={`${getPublicPrefix()}/bots/${item.id}`}
                className="text-left font-semibold text-customGreen  truncate"
              >
                {item.name}
              </Link>
              <span className="text-left text-gray-200  truncate">
                {formatDate(item.created)}
              </span>
              <span className="hidden md:block text-left text-gray-200  truncate">
                {item.type}
              </span>
              <Link href={`${getPublicPrefix()}/authors/${item.user.id}`}>
                <span className="bg-blue hidden sm:block text-left text-customGreen truncate ">
                  {item.user.username}
                </span>
              </Link>
            </div>
          </div>
        )}
      />
    </>
  );
}
