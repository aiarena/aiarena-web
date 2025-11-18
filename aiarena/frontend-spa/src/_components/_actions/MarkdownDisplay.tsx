import React from "react";
import MarkdownPreview from "@uiw/react-markdown-preview";
import rehypeSanitize from "rehype-sanitize";

interface MarkdownDisplayProps {
  markdown: string;
  className?: string;
}

export const MarkdownDisplay: React.FC<MarkdownDisplayProps> = ({
  markdown,
}) => {
  const rehypePlugins = [rehypeSanitize];
  return (
    <div>
      <MarkdownPreview
        rehypePlugins={rehypePlugins}
        style={{ padding: 16 }}
        source={markdown}
        components={{
          div: ({ children }) => <div className="">{children}</div>,

          a: ({ children, href }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      />
    </div>
  );
};
