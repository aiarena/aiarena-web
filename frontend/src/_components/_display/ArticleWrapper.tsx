import React, { ReactNode } from 'react';

interface ArticleWrapperProps {
  children: ReactNode;
  className?: string;
}

export default function ArticleWrapper({ children, className }: ArticleWrapperProps) {
  return (
    <div className={`${className} text-white  max-w-4xl m-auto p-4 mt-4 mb-8`}>
      {children}
    </div>
  );
}
