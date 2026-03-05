import Modal from "@/_components/_actions/Modal";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { useState } from "react";
import { Tag } from "./BotResultsTable";
import { Link } from "react-router";
import useParseUtils from "@/_components/_hooks/useParseUtils";

type TagSummaryWithModalProps = {
  tagNodes: Tag[];
  title?: string;
  previewCount?: number;
  className?: string;
  emptyText?: string;
};

export default function TagSummaryWithModal({
  tagNodes,
  title = "Tags",
  previewCount = 3,
  className = "",
}: TagSummaryWithModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const parseUtils = useParseUtils({ tagNodes });

  const cleanTags = parseUtils.cleanTags;
  const grouped = parseUtils.grouped;

  const preview = cleanTags.slice(0, previewCount);
  const label =
    cleanTags.length > 0 ? `[${cleanTags.length}] ${preview.join(", ")}` : "";
  const fullTitle = cleanTags.join(", ");

  return (
    <>
      <button
        type="button"
        className={[
          "text-left text-customGreen hover:underline underline-offset-2",
          "truncate max-w-[260px] align-middle",
          className,
        ].join(" ")}
        title={fullTitle}
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
      </Modal>
    </>
  );
}
