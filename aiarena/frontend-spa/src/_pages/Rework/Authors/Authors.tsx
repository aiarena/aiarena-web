import { Suspense, useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { AuthorsQuery } from "./__generated__/AuthorsQuery.graphql";
import Dropdown from "@/_components/_actions/Dropdown";
import DropdownButton from "@/_components/_actions/DropdownButton";
import Searchbar from "@/_components/_actions/Searchbar";
import AuthorsList from "./AuthorsList";

export default function Authors() {
  const data = useLazyLoadQuery<AuthorsQuery>(
    graphql`
      query AuthorsQuery {
        ...AuthorsList_node
      }
    `,
    {},
  );
  const [searchBarValue, setSearchBarValue] = useState("");
  const [orderBy, setOrderBy] = useState({ display: "Order By", value: "" });
  return (
    <>
      <section aria-labelledby="authors-heading">
        <div className="flex flex-wrap-reverse w-fullitems-start">
          {/* Display active competition limit and current active competitions */}
          <div
            className="flex gap-4 ml-auto mb-4"
            role="group"
            aria-label="Author filtering and sorting controls"
          >
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

        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <AuthorsList
            authors={data}
            searchBarValue={searchBarValue}
            orderBy={orderBy.value}
          />
        </Suspense>
      </section>
    </>
  );
}
