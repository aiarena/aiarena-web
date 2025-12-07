import { graphql, useFragment } from "react-relay";
import { getDateToLocale } from "@/_lib/dateUtils";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";
import { AuthorProfile_user$key } from "./__generated__/AuthorProfile_user.graphql";
import { getNodes } from "@/_lib/relayHelpers";

export interface AuthorProps {
  author: AuthorProfile_user$key;
}

export default function AuthorProfile(props: AuthorProps) {
  const author = useFragment(
    graphql`
      fragment AuthorProfile_user on UserType {
        id
        username
        patreonLevel
        dateJoined
        ...AvatarWithBorder_user
        bots {
          edges {
            node {
              trophies {
                edges {
                  node {
                    name
                    trophyIconName
                    trophyIconImage
                  }
                }
              }
            }
          }
        }
      }
    `,
    props.author
  );
  const bots = getNodes(author?.bots);
  const trophies = bots.flatMap((bot) => getNodes(bot.trophies));

  return (
    <div className="relative w-full rounded-lg border border-neutral-800 bg-darken-2 text-white shadow-lg shadow-black backdrop-blur p-2 mb-8">
      {author?.patreonLevel && author.patreonLevel !== "NONE" && (
        <div className="absolute -top-3 -right-2">
          <span className="inline-block rounded-full bg-neutral-900 shadow-black border-customGreen border-1 px-2 py-0.5 text-xs font-medium text-customGreen">
            Supporter
          </span>
        </div>
      )}

      <div className="flex items-start gap-2">
        <div className="flex flex-col items-center">
          <AvatarWithBorder user={author} size="lg" />
        </div>

        <div className="flex flex-col justify-between flex-1 ml-4 mr-8  min-w-0">
          <div className="min-w-0">
            <h2 className="text-xl sm:text-2xl font-semibold truncate max-w-full">
              {author.username}
            </h2>
            <p>
              <span className="font-small text-sm text-gray-300">Joined:</span>{" "}
              <span className="font-small text-sm text-gray-300">
                {getDateToLocale(author.dateJoined)}
              </span>
            </p>
          </div>

          <div className="mt-3 space-y-1 text-md text-gray-300">
            <p>
              {trophies.length > 0 && (
                <span className="font-medium text-white">
                  Total Trophies: {trophies.length}
                </span>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
