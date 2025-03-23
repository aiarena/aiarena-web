import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import React, { useState } from "react";
import { graphql, useFragment } from "react-relay";
import { AvatarWithBorder_user$key } from "./__generated__/AvatarWithBorder_user.graphql";

type AvatarWithBorderSizes = "sm" | "lg";

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
        avatar: 75,
        border: 85,
        marginRight: 5,
        marginTop: 3,
      },
      lg: {
        avatar: 150,
        border: 170,
        marginRight: 10,
        marginTop: 4,
      },
    };

    const returnSize = sizes[size];

    return returnSize;
  };

  const avatarSize = getAvatarSize(props.size);

  return (
    <div
      className={`p-3 relative w-[${avatarSize.border}px] h-[${avatarSize.border}px] flex items-center justify-center`}
    >
      <div
        className={`mr-[${avatarSize.marginRight}px] mt-[${avatarSize.marginTop}px] w-[${avatarSize.avatar}px] h-[${avatarSize.avatar}px] bg-white overflow-hidden `}
      >
        <img
          src={user?.avatarUrl || `${getPublicPrefix()}/${defaultAvatar}`}
          alt="User avatar"
          width={avatarSize.avatar}
          height={avatarSize.avatar}
        />
      </div>

      {user.patreonLevel && user.patreonLevel != "NONE" ? (
        <img
          src={`/frames/${user.patreonLevel.toLocaleLowerCase()}.png`}
          alt={`${formatBorder(user.patreonLevel)} frame`}
          width={avatarSize.border}
          height={avatarSize.border}
          className={`absolute w-[${avatarSize.border}px] h-[${avatarSize.border}px] object-contain pointer-events-none`}
        />
      ) : null}
    </div>
  );
}
