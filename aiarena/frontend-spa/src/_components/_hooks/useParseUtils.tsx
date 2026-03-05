import { Tag } from "@/_pages/Rework/Bot/BotResultsTable/BotResultsTable";
import { useMemo } from "react";

export default function useParseUtils({ tagNodes }: { tagNodes: Tag[] }) {
  const cleanNodes = useMemo(() => {
    return (tagNodes ?? [])
      .map((n) => ({
        ...n,
        tag: typeof n?.tag === "string" ? n.tag.trim() : "",
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
          acc[userId] = { user: t.user ?? null, tags: [] as typeof cleanNodes };
        }
        acc[userId].tags.push(t);
        return acc;
      },
      {} as Record<
        string,
        {
          user: { id: string; username: string } | null;
          tags: typeof cleanNodes;
        }
      >,
    );
  }, [cleanNodes]);
  return { grouped, cleanTags };
}
