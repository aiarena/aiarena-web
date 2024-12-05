import React, { ReactNode } from 'react';

interface ArticleWrapperProps {
  children: ReactNode;
}

export default function ArticleWrapper({ children }: ArticleWrapperProps) {
  return (
    <div className="text-white bg-slate-900 max-w-4xl m-auto p-4">
      {children}
    </div>
  );
}
