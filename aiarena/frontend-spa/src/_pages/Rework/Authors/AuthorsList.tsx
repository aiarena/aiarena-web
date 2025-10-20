import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { graphql, usePaginationFragment } from "react-relay";
import { AuthorsList_node$key } from "./__generated__/AuthorsList_node.graphql";
import { startTransition, useEffect } from "react";
import { useInfiniteScroll } from "@/_components/_hooks/useInfiniteScroll";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import LoadingMoreItems from "@/_components/_display/LoadingMoreItems";
import NoMoreItems from "@/_components/_display/NoMoreItems";
import Author from "./Author";

interface AuthorsListProps {
  authors: AuthorsList_node$key;
  searchBarValue: string;
  orderBy: string;
}

export default function AuthorsList(props: AuthorsListProps) {
  const {
    data: userData,
    loadNext,
    hasNext,
    refetch,
  } = usePaginationFragment(
    graphql`
      fragment AuthorsList_node on Query
      @refetchable(queryName: "AuthorsListPaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 20 }
        username: { type: "String" }
        orderBy: { type: "String" }
      ) {
        users(
          first: $first
          after: $cursor
          username: $username
          orderBy: $orderBy
          type: WEBSITE_USER
        ) @connection(key: "AuthorsList_node_users") {
          edges {
            node {
              id
              ...Author_user
            }
          }
        }
      }
    `,

    props.authors as AuthorsList_node$key,
  );

  useEffect(() => {
    startTransition(() => {
      refetch({ username: props.searchBarValue, orderBy: props.orderBy });
    });
  }, [props.searchBarValue, props.orderBy, refetch]);

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(20), hasNext);
  const users = getNodes(userData?.users);
  const hasItems = users.length > 0;

  return (
    <div
      role="region"
      aria-labelledby="authors-list-heading"
      aria-live="polite"
    >
      <h2 id="authors-list-heading" className="sr-only">
        Authors List
      </h2>
      {hasItems ? (
        <ul className="flex flex-wrap gap-12">
          {users.map((author) => (
            <li
              key={author.id}
              id={author.id}
              role="listitem"
              className="w-full sm:flex-[1_1_30rem] xl:max-w-[42rem]"
            >
              <a href={`/authors/${getIDFromBase64(author.id, "UserType")}`}>
                <Author author={author} />
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <NoItemsInListMessage>
          <p>No authors matched the search parameters...</p>
        </NoItemsInListMessage>
      )}
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more authors..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
