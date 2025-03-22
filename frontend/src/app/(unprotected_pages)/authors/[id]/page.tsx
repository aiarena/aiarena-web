"use client";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";
import { useUser } from "@/_components/_hooks/useUser";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import { notFound } from "next/navigation";

import React, { useEffect } from "react";

interface AuthorPageProps {
  params: {
    id: string;
  };
}

export default function Page({ params }: AuthorPageProps) {
  const author = useUser(decodeURIComponent(params.id));

  if (author === null) {
    notFound();
  }
  return (
    <>
      <ArticleWrapper className="bg-customBackgroundColor2 text-white">
        <section>
          <h1>{author?.username}</h1>
          <h1>{author?.patreonLevel}</h1>
          <p>Joined: {author?.dateJoined}</p>
          <p>ImgSRC : {author?.avatarUrl}</p>

          <AvatarWithBorder
            avatarSrc={author.avatarUrl}
            border={author.patreonLevel}
          />

          {author?.ownBots && author.ownBots.length > 0 ? (
            <ul>
              {author.ownBots.map((bot) => (
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
