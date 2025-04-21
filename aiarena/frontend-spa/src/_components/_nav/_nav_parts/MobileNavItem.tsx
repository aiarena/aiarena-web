import React from "react";
import { Link } from "react-router";
// import Link from "next/link";

interface NavItemProps {
  href: string;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}
function MobileNavItem({ href, children, onClick, className }: NavItemProps) {
  return (
    <Link to={href} onClick={onClick}>
      <div
        className={`cursor-pointer text-xl px-6 py-5 text-center hover:bg-white md:hover:bg-transparent hover:text-black ${className}`}
      >
        {children}
      </div>
    </Link>
  );
}

export default MobileNavItem;
