import { useMemo } from "react";

export type ParsedTagUser = {
  id: string;
  username?: string | null | undefined;
} | null | undefined;

export type ParsedTag = {
  id: string;
  tag: string | null | undefined;
  user: ParsedTagUser;
};

type CleanTag = {
  id: string;
  tag: string;
  user: ParsedTagUser;
};

type GroupedTags = Record<
  string,
  {
    user: ParsedTagUser;
    tags: CleanTag[];
  }
>;

export default function useParseUtils({
  tagNodes,
}: {
  tagNodes: ReadonlyArray<ParsedTag | null | undefined>;
}) {
  const cleanNodes = useMemo(() => {
    return (tagNodes ?? [])
      .filter((n): n is ParsedTag => n !== null && n !== undefined)
      .map((n): CleanTag => ({
        ...n,
        tag: typeof n.tag === "string" ? n.tag.trim() : "",
      }))
      .filter((n) => n.tag.length > 0);
  }, [tagNodes]);

  const cleanTags = useMemo(
    () => cleanNodes.map((n) => n.tag as string),
    [cleanNodes],
  );

  const grouped = useMemo(() => {
    return cleanNodes.reduce(
      (acc, t) => {
        const userId = t.user?.id ?? "unknown";
        if (!acc[userId]) {
          acc[userId] = { user: t.user ?? null, tags: [] };
        }
        acc[userId].tags.push(t);
        return acc;
      },
      {} as GroupedTags,
    );
  }, [cleanNodes]);
  return { grouped, cleanTags };
}
