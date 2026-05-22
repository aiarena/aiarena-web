import { ReactNode, useEffect, useRef, useState } from "react";
import {
  createHighlighter,
  type Highlighter,
  type BundledLanguage,
  type BundledTheme,
} from "shiki";
import {
  ClipboardDocumentIcon,
  CheckIcon,
} from "@heroicons/react/20/solid";
import { useSnackbar } from "notistack";

const THEME: BundledTheme = "github-dark-default";
const LANGS: BundledLanguage[] = [
  "graphql",
  "javascript",
  "typescript",
  "python",
  "bash",
  "json",
  "yaml",
];

let highlighterPromise: Promise<Highlighter> | null = null;

function getHighlighter(): Promise<Highlighter> {
  if (!highlighterPromise) {
    highlighterPromise = createHighlighter({
      themes: [THEME],
      langs: LANGS,
    });
  }
  return highlighterPromise;
}

interface CodeBlockProps {
  code: string;
  lang: BundledLanguage;
  className?: string;
  /**
   * Additional controls rendered in the top-right chrome row, to the left
   * of the copy button. Used for things like a language picker.
   */
  topRight?: ReactNode;
}

export default function CodeBlock({
  code,
  lang,
  className,
  topRight,
}: CodeBlockProps) {
  const [html, setHtml] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const mountedRef = useRef(true);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    getHighlighter().then((hl) => {
      if (cancelled || !mountedRef.current) return;
      const rendered = hl.codeToHtml(code, { lang, theme: THEME });
      setHtml(rendered);
    });
    return () => {
      cancelled = true;
    };
  }, [code, lang]);

  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      enqueueSnackbar("Copied to clipboard");
      setTimeout(() => {
        if (mountedRef.current) setCopied(false);
      }, 1500);
    });
  };

  const chrome = (
    <div className="absolute top-2 right-2 z-10 flex items-center gap-2">
      {topRight}
      <button
        onClick={handleCopy}
        title="Copy"
        className="p-1.5 rounded bg-black/40 hover:bg-black/70 text-gray-200 hover:text-white opacity-70 hover:opacity-100 transition"
      >
        {copied ? (
          <CheckIcon className="h-4 w-4" />
        ) : (
          <ClipboardDocumentIcon className="h-4 w-4" />
        )}
      </button>
    </div>
  );

  if (html == null) {
    return (
      <div className={"relative " + (className ?? "")}>
        {chrome}
        <pre className="bg-black text-gray-200 font-mono text-xs rounded p-3 overflow-auto">
          <code>{code}</code>
        </pre>
      </div>
    );
  }

  return (
    <div className={"relative " + (className ?? "")}>
      {chrome}
      <div
        className="shiki-block text-xs rounded overflow-auto [&_pre]:p-3 [&_pre]:m-0"
        // shiki output is trusted: it comes from our own static strings
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}
