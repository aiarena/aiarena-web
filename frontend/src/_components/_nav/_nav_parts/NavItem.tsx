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

function NavItem({ href, children, onClick }: NavItemProps) {
  const pathname = usePathname();

  const normalizedHref = `${getPublicPrefix()}${href}`.replace(/\/+$/, "");
  const normalizedPathname = pathname.replace(/\/+$/, "");
  const isActive = normalizedPathname === normalizedHref;


  
  return (
    <div className="text-l p-2  text-center">
      <Link
        className={` hover:text-slate-300 text-white py-2 ${
          isActive ? "border-b-2 border-customGreen font-bold"  : ""
        }`}
        href={href}
        onClick={onClick}
      >
        {children}
      </Link>
    </div>
  );
}

export default NavItem;
