"use client";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import { useBot } from "@/_components/_hooks/useBot";
import { useBots } from "@/_components/_hooks/useBots";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { getSiteUrl } from "@/_lib/getSiteUrl";
import Link from "next/link";
import { notFound } from "next/navigation";
import React, { useEffect } from "react";

interface BotPageProps {
    params: {
      id: string;
    };
  }
  

export default function Page({ params }:BotPageProps) {

  const bot = useBot(decodeURIComponent(params.id)); 
  
  console.log(bot);
  console.log(params);
    
  if(!bot) {
    return notFound()
  }
  
  return <>
  <ArticleWrapper className="bg-customBackgroundColor2 text-white">
    <section>
        <h1>{bot.name}</h1>
        <p>
            Created: {bot.created},
      
        </p>

<p>
        Type: {bot.type},
        </p>
        <p>
        Author: <Link href={`${getPublicPrefix()}/authors/${bot.user.id}` } className="text-customGreen cursor-pointer">{bot.user.username}</Link>
        </p>
    </section>

  </ArticleWrapper>
  </>
}
