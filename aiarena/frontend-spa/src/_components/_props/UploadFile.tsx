import {
  ArrowUpOnSquareStackIcon,
  Square2StackIcon,
} from "@heroicons/react/24/outline";
import React, { useRef } from "react";

interface FileUploadProps {
  id?: string;
  accept?: string;
  file: File | null;
  setFile: (file: File | null) => void;
  required?: boolean;
  "aria-describedby"?: string;
}

export const UploadFile: React.FC<FileUploadProps> = ({
  id = "file-upload",
  accept = ".zip",
  file,
  setFile,
  required = false,
  "aria-describedby": ariaDescribedBy,
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

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLLabelElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="w-full">
      <label
        htmlFor={id}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        role="button"
        aria-label={
          file
            ? `Selected file: ${file.name}. Click to change.`
            : "Click to select file or drag and drop"
        }
        className={`block cursor-pointer rounded border-2 border-dashed p-6 text-center text-gray-300 transition focus:outline-none focus:ring-2 focus:ring-customGreen focus:ring-offset-2 focus:ring-offset-neutral-900
          ${file ? "border-customGreen bg-darken-3" : "border-neutral-500 bg-neutral-900 hover:border-customGreen hover:bg-neutral-800"}`}
      >
        {file ? (
          <>
            <Square2StackIcon
              className="mx-auto mb-2 h-6 w-6 text-customGreen"
              aria-hidden="true"
            />
            <p className="text-sm text-customGreen truncate" title={file.name}>
              {file.name}
            </p>
          </>
        ) : (
          <>
            <ArrowUpOnSquareStackIcon
              className="mx-auto mb-2 h-6 w-6 text-gray-400"
              aria-hidden="true"
            />
            <p className="text-sm">Click or drag & drop a file here</p>
          </>
        )}
        <input
          id={id}
          type="file"
          name="fileUpload"
          accept={accept}
          ref={fileInputRef}
          className="sr-only"
          required={required}
          aria-describedby={ariaDescribedBy}
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null);
          }}
        />
      </label>
    </div>
  );
};
