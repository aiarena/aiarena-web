import { Suspense, useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import { AuthorsQuery } from "./__generated__/AuthorsQuery.graphql";
import Dropdown from "@/_components/_actions/Dropdown";
import DropdownButton from "@/_components/_actions/DropdownButton";
import Searchbar from "@/_components/_actions/Searchbar";
import AuthorsList from "./AuthorsList";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import FetchError from "@/_components/_display/FetchError";
import DisplaySkeletonAuthorList from "@/_components/_display/_skeletons/DisplaySkeletonAuthorList";

export default function Authors() {
  const data = useLazyLoadQuery<AuthorsQuery>(
    graphql`
      query AuthorsQuery {
        ...AuthorsList_node
      }
    `,
    {}
  );
  const [searchBarValue, setSearchBarValue] = useState("");
  const [orderBy, setOrderBy] = useState({ display: "Order By", value: "" });
  const [onlyWithBots, setOnlyWithBots] = useState(true);

  if (!data) {
    return <FetchError type="authors" />;
  }

  return (
    <>
      <section aria-labelledby="authors-heading">
        <div className="flex flex-wrap-reverse w-full items-start">
          <div
            className="flex gap-4 ml-auto mb-8 flex-wrap"
            role="group"
            aria-label="Author filtering and sorting controls"
          >
            <div className="flex items-center gap-2">
              <label
                htmlFor="downloadable-toggle"
                className="text-sm font-medium text-gray-300"
              >
                Only Authors with Bots
              </label>
              <SimpleToggle enabled={onlyWithBots} onChange={setOnlyWithBots} />
            </div>
            <Dropdown title={orderBy.display}>
              <DropdownButton
                onClick={() =>
                  setOrderBy({
                    display: "Date Joined",
                    value: "-date_joined",
                  })
                }
                title={"Date Joined"}
              />

              <DropdownButton
                onClick={() =>
                  setOrderBy({
                    display: "Username",
                    value: "username",
                  })
                }
                title={"Username"}
              />
            </Dropdown>
            <Searchbar
              onChange={setSearchBarValue}
              value={searchBarValue}
              placeholder="Search all authors..."
              aria-label="Search author by name"
            />
          </div>
        </div>

        <Suspense fallback={<DisplaySkeletonAuthorList />}>
          <AuthorsList
            authors={data}
            searchBarValue={searchBarValue}
            orderBy={orderBy.value}
            onlyWithBots={onlyWithBots}
          />
        </Suspense>
      </section>
    </>
  );
}
