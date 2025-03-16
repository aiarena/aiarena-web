"use client";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import { useUser } from "@/_components/_hooks/useUser";

import React, { useEffect } from "react";

interface AuthorPageProps {
  params: {
    id: string;
  };
}

export default function Page({ params }: AuthorPageProps) {
  const author = useUser(decodeURIComponent(params.id));

  return (
    <>
      <ArticleWrapper className="bg-customBackgroundColor2 text-white">
        <section>
          <h1>{author?.username}</h1>
          <h1>{author?.patreonLevel}</h1>
        </section>
      </ArticleWrapper>
    </>
  );
}
