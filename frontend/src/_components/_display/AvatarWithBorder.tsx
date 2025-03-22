import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import Image from "next/image";
import React from "react";

export type Border =
  | "NONE"
  | "BRONZE"
  | "SILVER"
  | "GOLD"
  | "PLATINUM"
  | "DIAMOND";

export interface AvatarWithBorderProps {
  avatarSrc?: string;
  border?: string;
}

export default function AvatarWithBorder({
  avatarSrc,
  border = "NONE",
}: AvatarWithBorderProps) {
  const isValidBorder = (border: string): border is Border =>
    ["NONE", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND"].includes(
      border,
    );

  const formatBorder = (border: string): string => {
    const lowerCased = border.toLowerCase();
    return lowerCased.charAt(0).toUpperCase() + lowerCased.slice(1);
  };

  return (
    <div className="relative w-[170px] h-[170px] flex items-center justify-center">
      {/* Avatar Image (150x150) */}
      <div className="mr-[10px] w-[150px] h-[150px] bg-white overflow-hidden">
        <Image
          src={
            avatarSrc
              ? "http://localhost:8000/media/avatars/2023/resized/80/80/unnamed.png"
              : `${getPublicPrefix()}/assets_logo/img/default_avatar.jpg`
          }
          alt="User avatar"
          width={150}
          height={150}
          className="object-cover w-full h-full "
        />
      </div>

      {border && isValidBorder(border) && border != "NONE" ? (
        <Image
          src={`${getPublicPrefix()}/frames/${border.toLocaleLowerCase()}.png`}
          alt={`${formatBorder(border)} frame`}
          width={170}
          height={170}
          className="absolute inset-0 w-[170px] h-[170px] object-contain pointer-events-none"
        />
      ) : (
        <></>
      )}
    </div>
  );
}
