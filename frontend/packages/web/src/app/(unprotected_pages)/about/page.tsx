"use client";
import React from "react";
import { graphql } from "relay-runtime";
import {useLazyLoadQuery} from "react-relay";
import { pageAboutQuery } from "./__generated__/pageAboutQuery.graphql";


// Utility to extract nodes safely from the connection
export function nodes<T>(connection: { edges: ReadonlyArray<{ node: T | null | undefined } | null | undefined> } | null | undefined): T[] {
  if (!connection || !connection.edges) return [];
  return connection.edges
    .filter((edge): edge is { node: T } => edge !== null && edge !== undefined && edge.node !== null && edge.node !== undefined)
    .map((edge) => edge.node);
}

function Page() {
  const data = useLazyLoadQuery<pageAboutQuery>(
      graphql`
        query pageAboutQuery {
          news(last: 5) {
            edges {
              node {
                id
                title
                text
              }
            }
          }
        }
      `,
      {},
  );
  return (
      <>
      {nodes(data.news).map((newsItem) => <div key={newsItem.id}>{newsItem.title}</div>)}

      <div className="text-center">
        <h1 className="text-4xl font-bold">What is AI Arena?</h1>
        <p className="text-lg mt-4">
          The AI Arena ladder provides an environment where Scripted and Deep
          Learning AIs fight in Starcraft 2. Matches are run 24/7 and streamed
          to various live-stream platforms. TwtichLink
        </p>
      </div>

      <div className="text-center">
        <h1 className="text-4xl font-bold">Updates: ? </h1>
        <p className="text-lg mt-4">
          List of latest updates
        </p>
      </div>
    </>
  );
}

export default Page;
