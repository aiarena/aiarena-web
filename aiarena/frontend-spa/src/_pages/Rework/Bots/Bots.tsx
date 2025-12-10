import { Suspense, useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";

import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { BotsQuery } from "./__generated__/BotsQuery.graphql";
import Searchbar from "@/_components/_actions/Searchbar";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import BotsTable from "./BotsTable";
import FetchError from "@/_components/_display/FetchError";

export default function Bots() {
  const data = useLazyLoadQuery<BotsQuery>(
    graphql`
      query BotsQuery {
        ...BotsTable_node
      }
    `,
    {}
  );
  const [searchBarValue, setSearchBarValue] = useState("");
  const [onlyDownloadable, setOnlyDownloadable] = useState(false);

  if (!data) {
    return <FetchError type="bots" />;
  }

  return (
    <>
      <section aria-labelledby="bots-heading">
        <h2 id="bots-heading" className="sr-only">
          Bots
        </h2>

        <Suspense fallback={<LoadingSpinner color="light-gray" />}>
          <BotsTable
            data={data}
            searchBarValue={searchBarValue}
            onlyDownloadable={onlyDownloadable}
            appendHeader={
              <div
                className="flex gap-4 items-center"
                role="group"
                aria-label="Bot filtering controls"
              >
                <div className="flex items-center gap-2">
                  <label
                    htmlFor="downloadable-toggle"
                    className="text-sm font-medium text-gray-300"
                  >
                    Only downloadable
                  </label>
                  <SimpleToggle
                    enabled={onlyDownloadable}
                    onChange={setOnlyDownloadable}
                  />
                </div>
                <Searchbar
                  onChange={setSearchBarValue}
                  value={searchBarValue}
                  placeholder="Search bots by name or author..."
                  aria-label="Search bot by name or author"
                  classNames="min-w-70"
                />
              </div>
            }
          />
        </Suspense>
      </section>
    </>
  );
}
