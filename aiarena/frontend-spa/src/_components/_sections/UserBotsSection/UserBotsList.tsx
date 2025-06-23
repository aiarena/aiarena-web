import { getNodes } from "@/_lib/relayHelpers";

import UserBot from "../../_display/userbot/UserBot";
import { graphql, usePaginationFragment } from "react-relay";
import { useInfiniteScroll } from "../../_hooks/useInfiniteScroll";

import { useDebouncedQuery } from "../../_hooks/useDebouncedQuery";
import LoadingMoreItems from "../../_display/LoadingMoreItems";
import NoMoreItems from "../../_display/NoMoreItems";
import { useRegisterConnectionID } from "../../_hooks/useRegisterRelayConnectionID";
import { CONNECTION_KEYS } from "../../_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";
import { startTransition } from "react";
import { UserBotsList_user$key } from "./__generated__/UserBotsList_user.graphql";
import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { socialLinks } from "@/_data/socialLinks";
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
          __id
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

  useRegisterConnectionID(
    CONNECTION_KEYS.UserBotsConnection,
    userData?.bots?.__id
  );

  useDebouncedQuery(
    props.searchBarValue,
    props.orderBy,
    500,
    (value, orderBy) => {
      startTransition(() => {
        refetch({ name: value, orderBy: orderBy });
      });
    },
    props.onLoadingChange
  );

  const { loadMoreRef } = useInfiniteScroll(() => loadNext(20), hasNext);
  const bots = getNodes(userData?.bots);
  const hasItems = bots.length > 0;

  return (
    <div role="region" aria-labelledby="bots-list-heading" aria-live="polite">
      <h2 id="bots-list-heading" className="sr-only">
        Your Agents List
      </h2>
      {hasItems ? (
        <ul className="space-y-12">
          {bots.map((bot) => (
            <li key={bot.id} id={bot.id} role="listitem">
              <UserBot bot={bot} />
            </li>
          ))}
        </ul>
      ) : (
        <NoItemsInListMessage>
          {/* <p>Looks like you don&rsquo;t have any bots yet.</p> */}
          <p>
            Your bots will appear here once you've uploaded them. <br />
            Visit our{" "}
            <a href={socialLinks["discord"]} target="_blank">
              Discord
            </a>{" "}
            or our{" "}
            <a
              href={"https://aiarena.net/wiki/bot-development/getting-started/"}
              target="_blank"
            >
              wiki
            </a>{" "}
            to get tips on how to get started.
          </p>
        </NoItemsInListMessage>
      )}
      {hasNext ? (
        <div className="flex justify-center mt-6" ref={loadMoreRef}>
          <LoadingMoreItems loadingMessage="Loading more bots..." />
        </div>
      ) : !hasNext && hasItems ? (
        <div className="mt-8">
          <NoMoreItems />
        </div>
      ) : null}
    </div>
  );
}
