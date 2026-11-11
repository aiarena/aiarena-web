// Wiki articles are django-wiki content pages, not named routes in `urls.py`,
// so they can't go through `reverseUrl`. Keep their paths here, in one place.
const WIKI_ARTICLES = {
  botZip: "/wiki/bot-development/getting-started/#wiki-toc-bot-zip",
  botData: "/wiki/bot-development/getting-started/#wiki-toc-bot-data",
} as const;

interface WikiLinkProps {
  article: keyof typeof WIKI_ARTICLES;
  className?: string;
}

/** Opens the relevant wiki section in a new tab. */
export default function WikiLink({ article, className }: WikiLinkProps) {
  return (
    <a href={WIKI_ARTICLES[article]} target="_blank" className={className}>
      Wiki
    </a>
  );
}
