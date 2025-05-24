import { ArrowUpOnSquareStackIcon } from "@heroicons/react/24/outline";
import React, { useRef } from "react";

interface FileUploadProps {
  accept?: string;
  file: File | null;
  setFile: (file: File | null) => void;
  required?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  accept = ".zip",
  file,
  setFile,
  required = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile && fileInputRef.current) {
      setFile(droppedFile);

      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(droppedFile);
      fileInputRef.current.files = dataTransfer.files;
    }
  };

  return (
    <label className="block w-full relative">
      <label
        htmlFor="file-upload"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`mt-2 block  cursor-pointer rounded border-2 border-dashed p-6 text-center text-gray-300 transition
          ${file ? "border-customGreen bg-darken-3" : "border-neutral-500 bg-neutral-900 hover:border-customGreen hover:bg-neutral-800"}`}
      >
        {file ? (
          <p className="text-sm truncate">{file.name}</p>
        ) : (
          <>
            <ArrowUpOnSquareStackIcon className="mx-auto mb-2 h-6 w-6 text-gray-400" />
            <p className="text-sm">Click or drag & drop a file here</p>
          </>
        )}
        <input
          id="file-upload"
          type="file"
          name="fileUpload"
          accept={accept}
          ref={fileInputRef}
          className="sr-only"
          required={required}
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null);
          }}
        />
      </label>
    </label>
  );
};
