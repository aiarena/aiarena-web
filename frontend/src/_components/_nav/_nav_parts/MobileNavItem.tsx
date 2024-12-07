"use client";
import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";

interface NavItemProps {
  href: string;
  children: React.ReactNode;
  onClick?: () => void;
}
function MobileNavItem({ href, children, onClick }: NavItemProps) {
  const pathname = usePathname();

  const normalizedHref = `${getPublicPrefix()}${href}`.replace(/\/+$/, "");
  const normalizedPathname = pathname.replace(/\/+$/, "");
  const isActive = normalizedPathname === normalizedHref;

  return (
    <Link href={href} onClick={onClick}>
      <div
        className={`cursor-pointer text-xl px-6 py-5 text-center hover:bg-white md:hover:bg-transparent hover:text-black ${
          isActive ? "border-y-2 border-customGreen" : "border-none"
        }`}
      >
        {children}
      </div>
    </Link>
  );
}

export default MobileNavItem;