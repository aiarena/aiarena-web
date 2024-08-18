"use client"
import React, { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { request_post } from "../_lib/fetchTools";
import { postFile } from "../_lib/fileTools";
import { useSession } from "next-auth/react";
import { secure_request_post } from "@/_lib/secureFetchTools";

export default function NewNote() {
  const file = React.useRef(null);
  const [content, setContent] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const router = useRouter();
  const session = useSession();
  const secret = (session.data?.user)?.token;

  async function DoSomething() {
    const data = await s3Upload();
    console.log(data);
  }

  function validateForm() {
    return content.length > 0;
  }

  function handleFileChange(event) {
    file.current = event.target.files[0];
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (file.current && file.current.size > 5000000) {
      alert(`Please pick a file smaller than ${5000000 / 1000000} MB.`);
      return;
    }
    console.log("submitting");
    setIsLoading(true);
    // router.push("/");
    try {
      // const attachment = file.current ? await s3Upload(file.current) : null;
      const attachmentFile = file.current ? await postFile({ file }) : null;
     
      const attachment = attachmentFile.data.id 
      console.log(attachmentFile)
      // const attachment = file.current ? await s3Upload() : null;
      // const attachment = null;

      await createNote( content, attachment );
      setIsLoading(false);
      // nav("/");
    } catch (error) {
      // onError(e);
      console.log(error);
      setIsLoading(false);
    }
  }

  async function createNote(data, attachment) {
    console.log("Sending request post in newNote")

    return secure_request_post({
      path: `notes`,
      // url: `${process.env.NEXT_PUBLIC_URL}/api/note`,
      data: JSON.stringify({ content: data, attachment: attachment }),
    });
  }

  return (
    <div className="NewNote">
      <form onSubmit={handleSubmit}>
        <div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <div>
          <label>Attachment</label>
          <input onChange={handleFileChange} type="file" />
        </div>
        <button type="submit" disabled={!validateForm()}>
          {isLoading ? "Loading..." : "Create"}
        </button>
      </form>
      <button
        onClick={() => {
          DoSomething();
        }}
      >
        Something Debug
      </button>
    </div>
  );
}
