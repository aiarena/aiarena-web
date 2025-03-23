"use client";
import { Suspense } from "react";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import { formatDateISO } from "@/_lib/dateUtils";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Link from "next/link";
import { getBotBasic } from "@/_components/_hooks/useExperimentalBotSSR";
import BotParticipations from "./BotParticipations";
import { notFound } from "next/navigation";
import { graphql, useLazyLoadQuery } from "react-relay";
import { pageBotQuery } from "./__generated__/pageBotQuery.graphql";

interface BotPageProps {
  params: {
    id: string;
  };
}

export default function Page(props: BotPageProps) {
  const bot = useLazyLoadQuery<pageBotQuery>(
    graphql`
      query pageBotQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            id
            name
            type
            created
            botZipUpdated
            wikiArticle
            user {
              id
              username
            }
          }
        }
      }
    `,
    { id: decodeURIComponent(props.params.id) }
  );

  if (!bot.node) {
    notFound();
  }

  return (
    <ArticleWrapper className="bg-customBackgroundColor2 text-white">
      <section>
        {/* Server-rendered basic bot information */}
        <h1>{bot.node.name}</h1>
        <p>Created: {formatDateISO(bot.node.created)}</p>
        <p>Last updated: {formatDateISO(bot.node.botZipUpdated)}</p>
        <p>Type: {bot.node.type}</p>
        <p>
          Author:{" "}
          <Link
            href={`${getPublicPrefix()}/authors/${bot.node.user?.id}`}
            className="text-customGreen cursor-pointer"
          >
            {bot.node.user?.username}
          </Link>
        </p>
        <p>Wiki Article: {bot.node.wikiArticle}</p>

        {/* Client-side rendered participations with Suspense boundary */}
        <Suspense fallback={<div>Loading match and competition data...</div>}>
          {bot.node.id && <BotParticipations botId={bot.node.id} />}
        </Suspense>
      </section>
    </ArticleWrapper>
  );
}
