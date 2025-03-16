"use client";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
// import { useUser } from "@/_components/_hooks/useUser";

import React, { useEffect } from "react";


interface AuthorPageProps {
    params: {
      id: string;
    };
  }
  

export default function Page({ params }: AuthorPageProps) {
    // const author = useAuthor(decodeURIComponent(params.id))
    // decodeURIComponent(params.id)

  //  const user = useUser()
  //  user?.patreonLevel

    useEffect(() => {
        console.log("Par",params);
    }, [params])
    
  
  return <>
  <ArticleWrapper className="bg-customBackgroundColor2 text-white">
    <section>
        {/* <h1>{author?.username}</h1> */}
    </section>

  </ArticleWrapper>
  </>;
}
