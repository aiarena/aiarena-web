import useParseUtils from "@/_components/_hooks/useParseUtils";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import { MatchTagSection_match$key } from "./__generated__/MatchTagSection_match.graphql";

interface MatchTagSectionProps {
  match: MatchTagSection_match$key;
}

export default function MatchTagSection({
  match: matchKey,
}: MatchTagSectionProps) {
  const match = useFragment(
    graphql`
      fragment MatchTagSection_match on MatchType
      @argumentDefinitions(
        showEveryonesTags: { type: "Boolean!", defaultValue: false }
      ) {
        tags(showEveryonesTags: $showEveryonesTags) {
          edges {
            node {
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
    matchKey,
  );

  const tagNodes = getNodes(match.tags);
  const { grouped, cleanTags } = useParseUtils({ tagNodes });

  return (
    <section
      aria-labelledby="match-tags-heading"
      className="rounded-2xl border border-neutral-800 bg-darken-2 p-5 shadow-lg shadow-black backdrop-blur-sm"
    >
      <div className="mb-4 flex items-center gap-2">
        <h3
          id="match-tags-heading"
          className="text-lg font-semibold text-white sm:text-xl"
        >
          Tags
        </h3>

        {cleanTags.length > 0 && (
          <span className="text-sm text-gray-400">({cleanTags.length})</span>
        )}
      </div>

      {tagNodes.length === 0 ? (
        <p className="text-sm italic text-gray-400">
          No tags added for this match yet.
        </p>
      ) : (
        <div className="space-y-4">
          {Object.values(grouped).map(({ user, tags }) => (
            <div
              key={user?.id ?? "unknown"}
              className="rounded-md border border-neutral-700 bg-darken-2 p-3"
            >
              <div className="mb-2 flex items-center gap-2">
                <span className="font-semibold text-customGreen">
                  {user ? (
                    <Link
                      to={reverseUrl("author", {
                        pk: getIDFromBase64(user.id, "UserType"),
                      })}
                      className="hover:underline"
                    >
                      {user.username}
                    </Link>
                  ) : (
                    "Unknown User"
                  )}
                </span>

                <span className="text-sm text-gray-400">({tags.length})</span>
              </div>

              <ul className="flex flex-wrap">
                {tags.map((tag) => (
                  <li key={tag.id}>
                    <span className="m-[2px] inline-flex items-center rounded-full border border-neutral-700 bg-neutral-900/70 px-2 py-1 text-sm text-gray-200">
                      {tag.tag}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
