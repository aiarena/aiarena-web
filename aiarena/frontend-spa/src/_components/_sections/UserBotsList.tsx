import { getNodes } from "@/_lib/relayHelpers";

import UserBot from "../_display/userbot/UserBot";
import LoadingDots from "../_display/LoadingDots";
import { graphql, usePaginationFragment } from "react-relay";
import { useInfiniteScroll } from "../_hooks/useInfiniteScroll";

import { UserBotsList_user$key } from "./__generated__/UserBotsList_user.graphql";
import { useDebouncedSearch } from "../_hooks/useDebouncedSearch";

interface UserBotsListProps {
  user: UserBotsList_user$key;
  searchBarValue: string;
}

export default function UserBotsList(props: UserBotsListProps) {
  const {
    data: userData,
    loadNext,
    hasNext,
    isLoadingNext,
    refetch,
  } = usePaginationFragment(
    graphql`
      fragment UserBotsList_user on UserType
      @argumentDefinitions(
        cursor: { type: "String" }
        name: { type: "String" }
        first: { type: "Int", defaultValue: 20 }
      )
      @refetchable(queryName: "UserBotsListPaginationQuery") {
        bots(first: $first, after: $cursor, name: $name)
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

  useDebouncedSearch(props.searchBarValue, 500, (value) => {
    refetch({ name: value });
  });

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
      {(hasNext || isLoadingNext) && (
        <div className="flex justify-center mt-8" ref={loadMoreRef}>
          <LoadingDots />
        </div>
      )}
    </div>
  );
}
