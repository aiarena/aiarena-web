import React from "react";
import { createPortal } from "react-dom";

const Modal = ({ children, onClose, title }) => {
  return createPortal(
    <div
      className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-gray-800 text-white rounded-lg shadow-md w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="pb-6 px-2 pt-2 overflow-y-auto max-h-screen">
          <div className="flex items-center justify-between mb-4">
            <p className="text-customGreen text-lg font-bold ml-2">{title}</p>
            <button
              className="text-gray-400 hover:text-gray-200"
              onClick={onClose}
              aria-label="Close modal"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          <div className="p-4">{children}</div>
        </div>
      </div>
    </div>,
    document.body,
  );
};

export default Modal;
