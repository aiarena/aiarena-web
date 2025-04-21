import React from "react";
import { Link } from "react-router";
interface NavItemProps {
  href: string;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

function NavItem({ href, children, onClick, className }: NavItemProps) {
  return (
    <div className="text-l p-2  text-center">
      <Link
        className={`py-2 hover:text-slate-300 text-white ${className}`}
        to={href}
        onClick={onClick}
      >
        {children}
      </Link>
    </div>
  );
}

export default NavItem;
