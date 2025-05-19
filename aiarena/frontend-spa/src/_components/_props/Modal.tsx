import { ReactNode, useEffect } from "react";
import { createPortal } from "react-dom";
import SectionDivider from "../_display/SectionDivider";

interface ModalProps {
  children: ReactNode;
  onClose: () => void;
  isOpen: boolean;
  title: string;
  keepUnsetOnClose?: boolean;
  size?: "m" | "l";
}

const Modal = ({
  children,
  isOpen,
  onClose,
  title,
  keepUnsetOnClose,
  size = "m",
}: ModalProps) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      if (!keepUnsetOnClose) {
        document.body.style.overflow = "unset";
      }
    };
  }, [isOpen, keepUnsetOnClose]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 bg-darken-2 bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div
        className={` bg-gray-800 rounded-lg shadow-md w-full ${size == "m" ? "max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl" : null} ${size == "l" ? "max-w-screen" : null}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="pb-6 px-2 pt-2 max-h-screen">
          <div className="flex items-center justify-between pb-2">
            <p className="text-lg font-bold ml-2 truncate">{title}</p>

            <button
              className="text-gray-400 hover:text-gray-200"
              onClick={() => {
                onClose();
              }}
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
          <SectionDivider color="gray" className="mb-1" />
          <div className=" p-4 overflow-y-auto max-h-[90vh]">{children}</div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default Modal;
