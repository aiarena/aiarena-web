import Modal from "@/_components/_actions/Modal";
import useParseUtils from "@/_components/_hooks/useParseUtils";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { Link } from "react-router";
import { Suspense, useMemo, useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { TagSummaryModalQuery } from "./__generated__/TagSummaryModalQuery.graphql";

type TagSummaryWithModalProps = {
  matchId: string;
  tagCount: number;
  firstTag?: string;
  title?: string;
  className?: string;
};

type MatchTag = NonNullable<
  NonNullable<NonNullable<TagSummaryModalQuery["node"]>["tags"]>[number]
>;

function TagModalBody({ matchId }: { matchId: string }) {
  const data = useLazyLoadQuery<TagSummaryModalQuery>(
    graphql`
      query TagSummaryModalQuery($id: ID!) {
        node(id: $id) {
          ... on MatchType {
            tags {
              id
              tag
              user {
                id
                username
              }
            }
          }
        }
      }
    `,
    { id: matchId },
  );

  const tagNodes = useMemo(() => data.node?.tags ?? [], [data.node]) as MatchTag[];
  const parseUtils = useParseUtils({ tagNodes });
  const grouped = parseUtils.grouped;

  if (tagNodes.length === 0) {
    return <p className="text-sm text-gray-400 italic">No tags added for this match yet.</p>;
  }

  return (
    <div className="space-y-6">
      {Object.values(grouped).map(({ user, tags }) => (
        <div
          key={user?.id ?? "unknown"}
          className="space-y-2  bg-darken-2 p-2 border border-neutral-700 rounded-md"
        >
          <div className="flex items-center gap-2">
            <span className="font-semibold text-customGreen">
              {user ? (
                <Link
                  to={`/authors/${getIDFromBase64(user.id, "UserType")}`}
                  className="hover:underline"
                >
                  {user.username}
                </Link>
              ) : (
                "Unknown User"
              )}
            </span>

            <span>({tags.length})</span>
          </div>

          <ul className="flex flex-wrap">
            {tags.map((t) => (
              <li key={t.id}>
                <span className="inline-flex items-center rounded-full border border-neutral-700 bg-neutral-900/70 px-2 py-1 m-[2px] text-s text-gray-200">
                  {t.tag}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default function TagSummaryWithModal({
  matchId,
  tagCount,
  firstTag,
  title = "Tags",
  className = "",
}: TagSummaryWithModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const label = tagCount > 0 ? `[${tagCount}] ${firstTag ?? ""}` : "";

  return (
    <>
      <button
        type="button"
        className={[
          "text-left text-customGreen hover:underline underline-offset-2",
          "truncate max-w-[260px] align-middle",
          className,
        ].join(" ")}
        title={label}
        onClick={() => setIsOpen(true)}
      >
        {label}
      </button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title={title}
        size="m"
      >
        <Suspense fallback={<p className="text-sm text-gray-400">Loading tags...</p>}>
          {isOpen ? <TagModalBody matchId={matchId} /> : null}
        </Suspense>
      </Modal>
    </>
  );
}
