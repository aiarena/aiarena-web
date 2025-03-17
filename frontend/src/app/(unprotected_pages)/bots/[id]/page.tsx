import { Suspense } from 'react';
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import { formatDateISO } from "@/_lib/dateUtils";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Link from "next/link";
import { getBotBasic } from '@/_components/_hooks/useExperimentalBotSSR';
import BotParticipations from './BotParticipations';


interface BotPageProps {
  params: {
    id: string;
  };
}

// This is a Server Component
export default async function Page({ params }: BotPageProps) {
  const botId = decodeURIComponent(params.id);
  
  // Fetch basic bot data on the server
  const bot = await getBotBasic(botId);
  
  if (!bot) {
    return <div>Bot not found</div>;
  }

  return (
    <ArticleWrapper className="bg-customBackgroundColor2 text-white">
      <section>
        {/* Server-rendered basic bot information */}
        <h1>{bot.name}</h1>
        <p>Created: {formatDateISO(bot.created)}</p>
        <p>Last updated: {formatDateISO(bot.botZipUpdated)}</p>
        <p>Type: {bot.type}</p>
        <p>
          Author:{" "}
          <Link
            href={`${getPublicPrefix()}/authors/${bot.user.id}`}
            className="text-customGreen cursor-pointer"
          >
            {bot.user.username}
          </Link>
        </p>
        <p>Wiki Article: {bot.wikiArticle}</p>
        
        {/* Client-side rendered participations with Suspense boundary */}
        <Suspense fallback={<div>Loading match and competition data...</div>}>
          <BotParticipations botId={botId} />
        </Suspense>
      </section>
    </ArticleWrapper>
  );
}