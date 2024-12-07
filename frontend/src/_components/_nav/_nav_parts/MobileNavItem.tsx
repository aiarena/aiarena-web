"use client";
import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";

interface NavItemProps {
  href: string;
  children: React.ReactNode;
  onClick?: () => void;
}

function MobileNavItem({ href, children, onClick }: NavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      className={` ${isActive ? "font-bold" : ""}`}
      href={href}
      onClick={onClick}
    >
      <div className="cursor-pointer text-xl px-6 text-center py-5 hover:bg-white md:hover:bg-transparent hover:text-black">
        {children}
      </div>
    </Link>
  );
}

export default MobileNavItem;
