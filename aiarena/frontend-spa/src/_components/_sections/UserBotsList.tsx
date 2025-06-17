import { getNodes } from "@/_lib/relayHelpers";

import UserBot from "../_display/userbot/UserBot";
import { graphql, usePaginationFragment } from "react-relay";
import { useInfiniteScroll } from "../_hooks/useInfiniteScroll";

import { UserBotsList_user$key } from "./__generated__/UserBotsList_user.graphql";
import { useDebouncedQuery } from "../_hooks/useDebouncedSearch";
import LoadingMoreItems from "../_display/LoadingMoreItems";
import NoMoreItems from "../_display/NoMoreItems";
interface UserBotsListProps {
  user: UserBotsList_user$key;
  searchBarValue: string;
  orderBy: string;

  onLoadingChange: (isLoading: boolean) => void;
}

export default function UserBotsList(props: UserBotsListProps) {
  const {
    data: userData,
    loadNext,
    hasNext,
    refetch,
  } = usePaginationFragment(
    graphql`
      fragment UserBotsList_user on UserType
      @argumentDefinitions(
        cursor: { type: "String" }
        name: { type: "String" }
        orderBy: { type: "String" }
        first: { type: "Int", defaultValue: 20 }
      )
      @refetchable(queryName: "UserBotsListPaginationQuery") {
        bots(first: $first, after: $cursor, name: $name, orderBy: $orderBy)
          @connection(key: "UserBotsSection_user_bots") {
          edges {
            node {
              id
              ...UserBot_bot
            }
          }
        }
      }
    `,

    props.user as UserBotsList_user$key
  );

  useDebouncedQuery(
    props.searchBarValue,
    props.orderBy,
    500,
    (value, orderBy) => {
      refetch({ name: value, orderBy: orderBy });
    },
    props.onLoadingChange
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(20), hasNext);

  return (
    <div role="region" aria-labelledby="bots-list-heading" aria-live="polite">
      <h2 id="bots-list-heading" className="sr-only">
        Your Agents List
      </h2>

      <ul className="space-y-12">
        {getNodes(userData?.bots).map((bot) => (
          <li key={bot.id} id={bot.id} role="listitem">
            <UserBot bot={bot} />
          </li>
        ))}
      </ul>
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more bots..." />
        </div>
      ) : (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      )}
    </div>
  );
}
