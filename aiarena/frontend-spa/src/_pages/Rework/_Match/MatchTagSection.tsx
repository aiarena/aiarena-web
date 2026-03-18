import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { graphql, useFragment } from "react-relay";
import { MatchTagSection_match$key } from "./__generated__/MatchTagSection_match.graphql";
import useParseUtils from "@/_components/_hooks/useParseUtils";

interface MatchTagSectionProps {
  match: MatchTagSection_match$key;
}

export default function MatchTagSection(props: MatchTagSectionProps) {
  const match = useFragment(
    graphql`
      fragment MatchTagSection_match on MatchType {
        tags {
          edges {
            node {
              tag
              id
              user {
                id
                username
              }
            }
          }
        }
      }
    `,
    props.match,
  );
  const tagNodes = getNodes(match.tags);

  const parseUtils = useParseUtils({ tagNodes });

  return (
    <section
      aria-labelledby="match-tags-heading"
      className="rounded-2xl border border-neutral-800 bg-darken-2 p-5 shadow-lg shadow-black backdrop-blur-sm"
    >
      <h3 className="text-lg sm:text-xl font-semibold text-white mb-1">Tags</h3>

      {tagNodes.length === 0 && (
        <p className="text-sm text-gray-400 italic">
          No tags added for this match yet.
        </p>
      )}

      <div className="space-y-6">
        {Object.values(parseUtils.grouped).map(({ user, tags }) => (
          <div key={user?.id ?? "unknown"} className="space-y-2">
            <div className="flex items-center gap-2">
              <span className=" font-semibold text-customGreen">
                {user ? (
                  <a
                    href={`/authors/${getIDFromBase64(user.id, "UserType")}`}
                    className="hover:underline"
                  >
                    {user.username}
                  </a>
                ) : (
                  "Unknown User"
                )}
              </span>
            </div>

            <ul className="flex flex-wrap">
              {tags.map((tag) => (
                <li key={tag.id}>
                  <span className="inline-flex items-center rounded-full border border-neutral-700 bg-neutral-900/70 px-2 py-1 m-[2px] text-xs text-gray-200">
                    {tag.tag}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
