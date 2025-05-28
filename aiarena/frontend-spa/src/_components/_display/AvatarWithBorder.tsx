import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { graphql, useFragment } from "react-relay";
import { AvatarWithBorder_user$key } from "./__generated__/AvatarWithBorder_user.graphql";

type AvatarWithBorderSizes = "sm" | "lg" | "xl";

export interface AvatarWithBorderProps {
  size?: AvatarWithBorderSizes;
  user: AvatarWithBorder_user$key;
}

export default function AvatarWithBorder(props: AvatarWithBorderProps) {
  const user = useFragment(
    graphql`
      fragment AvatarWithBorder_user on UserType {
        patreonLevel
        avatarUrl
      }
    `,
    props.user
  );

  const defaultAvatar = `/user/default.jpg`;

  const formatBorder = (border: string): string => {
    const lowerCased = border.toLowerCase();
    return lowerCased.charAt(0).toUpperCase() + lowerCased.slice(1);
  };

  const getAvatarSize = (size: AvatarWithBorderSizes = "sm") => {
    const sizes = {
      sm: {
        avatar: 77,
        border: 88,
        moveBorderRight: 3,
        moveBorderUp: 2,
      },
      lg: {
        avatar: 150,
        border: 174,
        moveBorderRight: 6,
        moveBorderUp: 3,
      },
      xl: {
        avatar: 205,
        border: 236,
        moveBorderRight: 8,
        moveBorderUp: 4,
      },
    };

    const returnSize = sizes[size];

    return returnSize;
  };

  const avatarSize = getAvatarSize(props.size);

  return (
    <div className={`m-3 flex items-center justify-center`}>
      <div
        className={`w-[${avatarSize.avatar}px] h-[${avatarSize.avatar}px]  overflow-hidden `}
      >
        <img
          src={user?.avatarUrl || `${getPublicPrefix()}/${defaultAvatar}`}
          alt="User avatar"
          width={avatarSize.avatar}
          height={avatarSize.avatar}
          className="bg-white"
        />
      </div>

      {user.patreonLevel && user.patreonLevel != "NONE" ? (
        <img
          src={`${getPublicPrefix()}/frames/${user.patreonLevel.toLocaleLowerCase()}.png`}
          alt={`${formatBorder(user.patreonLevel)} frame`}
          width={avatarSize.border}
          height={avatarSize.border}
          className={`absolute w-[${avatarSize.border}px] h-[${avatarSize.border}px] object-contain pointer-events-none`}
          style={{
            transform: `translate(${avatarSize.moveBorderRight}px, -${avatarSize.moveBorderUp}px)`,
          }}
        />
      ) : null}
    </div>
  );
}
