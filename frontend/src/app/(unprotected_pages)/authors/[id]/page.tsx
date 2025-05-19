"use client";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";
import { notFound } from "next/navigation";

import React from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { pageAuthorQuery } from "./__generated__/pageAuthorQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import { formatDate } from "@/_lib/dateUtils";

interface AuthorPageProps {
  params: {
    id: string;
  };
}

export default function Page(props: AuthorPageProps) {
  const user = useLazyLoadQuery<pageAuthorQuery>(
    graphql`
      query pageAuthorQuery($id: ID!) {
        node(id: $id) {
          ... on UserType {
            username
            patreonLevel
            dateJoined
            bots {
              edges {
                node {
                  id
                  name
                  type
                  playsRace
                }
              }
              totalCount
            }
            ...AvatarWithBorder_user
          }
        }
      }
    `,
    { id: decodeURIComponent(props.params.id) }
  );

  if (!user.node) {
    notFound();
  }

  return (
    <>
      <ArticleWrapper className="bg-customBackgroundColor2 text-white">
        <section>
          <h1>{user.node?.username}</h1>
          <h1>{user.node?.patreonLevel}</h1>
          <p>Joined: {formatDate(user.node?.dateJoined)}</p>
          {user.node ? <AvatarWithBorder user={user.node} size="lg" /> : null}

          {user.node?.bots && user.node?.bots?.totalCount > 0 ? (
            <ul>
              {getNodes(user.node.bots).map((bot) => (
                <li key={bot.id} onClick={() => console.log(bot.id)}>
                  <p>Name: {bot.name}</p>
                  <p>Plays Race: {bot.playsRace}</p>
                  <p>Type: {bot.type}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>No bots available.</p>
          )}
        </section>
      </ArticleWrapper>
    </>
  );
}
