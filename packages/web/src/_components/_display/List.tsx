import Link from "next/link";
import React, { useEffect } from "react";

type Item = {
  createdAt: string; // Assuming createdAt is of string type, adjust if needed
  userId: string; // Assuming userId is of string type, adjust if needed
  content: string;
  sortKey: string;
  attachment: string;
  noteId: string;
  createdBy: string;
  // other post fields
};

type ItemProps = {
  id: string;
};

export default function List({ items }: { items: Item[] }) {
  useEffect(() => {

    console.log(items);

  }, [items]);

  return (
    <>
      {items && items.length > 0 ? (
        items.map((post, index) => (
          <Link href={`/note/${post.noteId}`} key={index}>
            <div className="border border-gray-500 rounded-lg p-4">
              <p>{post.createdAt}</p>
              <p>{post.userId}</p>
              <p>{post.content}</p>
              <p>{post.attachment}</p>
            </div>
          </Link>
        ))
      ) : (
        <></>
      )}
    </>
  );
}
