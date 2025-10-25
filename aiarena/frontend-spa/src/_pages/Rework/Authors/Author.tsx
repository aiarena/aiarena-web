import { graphql, useFragment } from "react-relay";
import { Author_user$key } from "./__generated__/Author_user.graphql";
import { getDateToLocale } from "@/_lib/dateUtils";
import AvatarWithBorder from "@/_components/_display/AvatarWithBorder";

export interface AuthorProps {
  author: Author_user$key;
}

export default function Author(props: AuthorProps) {
  const author = useFragment(
    graphql`
      fragment Author_user on UserType {
        id
        username
        patreonLevel
        dateJoined
        ...AvatarWithBorder_user
        bots {
          totalCount
        }
      }
    `,
    props.author
  );
  return (
    <div className="relative w-full rounded-lg border border-neutral-600 bg-neutral-900/60 text-white shadow-lg shadow-black backdrop-blur p-2 hover:border-customGreen">
      {author?.patreonLevel && author.patreonLevel !== "NONE" && (
        <div className="absolute -top-3 -right-2">
          <span className="inline-block rounded-full bg-neutral-900 shadow-black border-customGreen border-1 px-2 py-0.5 text-xs font-medium text-customGreen">
            Supporter
          </span>
        </div>
      )}

      <div className="flex items-start gap-2">
        <div className="flex flex-col items-center">
          <AvatarWithBorder user={author} size="sm" />
        </div>

        {/* Right side content */}
        <div className="flex flex-col justify-between flex-1 ml-4 mr-8">
          <div>
            <h3 className="text-lg font-semibold">{author.username}</h3>
            <p>
              <span className="font-small text-sm text-gray-300">Joined:</span>{" "}
              <span className="font-small text-sm text-gray-300">
                {getDateToLocale(author.dateJoined)}
              </span>
            </p>
          </div>

          <div className="mt-3 space-y-1 text-md text-gray-300">
            <p>
              <span className="font-medium text-white">Bots:</span>{" "}
              {author.bots?.totalCount ?? 0}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
