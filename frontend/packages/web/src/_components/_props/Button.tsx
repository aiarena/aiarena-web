import React from "react";
import Link from "next/link";

interface Button {
  url: string;
  text: string;
}

export default function Button({ url, text }: Button) {
  return (
    <Link href={`${url}`} className="bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 text-white font-bold py-2 px-6 rounded-lg shadow-lg transform hover:scale-105 transition-transform duration-300 break-words overflow-hidden max-w-xs">
      {text}
    </Link>
  );
}
