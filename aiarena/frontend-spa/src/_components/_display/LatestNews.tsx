import React, { useState } from "react";
import NewsBox from "./NewsBox";
import { graphql, useLazyLoadQuery } from "react-relay";
import { LatestNewsQuery } from "./__generated__/LatestNewsQuery.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import WrappedTitle from "./WrappedTitle";
import FetchError from "./FetchError";

const LatestNews: React.FC = () => {
  const data = useLazyLoadQuery<LatestNewsQuery>(
    graphql`
      query LatestNewsQuery {
        news {
          edges {
            node {
              id
              title
              text
              created
              ytLink
            }
          }
        }
      }
    `,
    {}
  );
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!data.news) {
    return <FetchError type="news" />;
  }

  const newsData = getNodes(data.news);

  const handleDotClick = (index: number) => {
    setCurrentIndex(index);
  };

  const currentNewsItem = newsData[currentIndex];

  return (
    <div>
      <WrappedTitle title="News" font="font-bold" />
      <div className="bg-darken">
        <div className="flex items-center justify-center relative mb-4 bg-customGreen-dark-2">
          <p className="font-bold text-center px-4 py-2 truncate">
            {currentNewsItem.title}
          </p>
        </div>
        <div className="m-4">
          <p className="text-sm break-words h-8 overflow-hidden line-clamp-3">
            {new Date(currentNewsItem.created).toLocaleDateString()}
          </p>
          <p className="text-sm break-words h-16 overflow-hidden line-clamp-3">
            {currentNewsItem.text}
          </p>
        </div>
        <NewsBox key={currentNewsItem.id} videoUrl={currentNewsItem.ytLink} />
      </div>
      <div className="flex items-center justify-center mt-4">
        {newsData.map((_, index) => (
          <button
            key={index}
            onClick={() => handleDotClick(index)}
            className={`w-4 h-4 rounded-full mx-1 transition duration-100 ${
              currentIndex === index
                ? "bg-customGreen shadow shadow-black"
                : "bg-gray-400"
            }`}
          ></button>
        ))}
      </div>
    </div>
  );
};

export default LatestNews;
