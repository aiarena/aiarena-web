import { ReactNode, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import clsx from "clsx";
import SectionDivider from "../_display/SectionDivider";
import BackgroundTexture from "../_display/BackgroundTexture";

interface ModalProps {
  children: ReactNode;
  onClose: () => void;
  isOpen: boolean;
  title: string;
  keepUnsetOnClose?: boolean;
  size?: "m" | "l";
  padding?: number;
  paddingX?: number;
}

const Modal = ({
  children,
  isOpen,
  onClose,
  title,
  keepUnsetOnClose,
  size = "m",
  padding = 4,
  paddingX = 6,
}: ModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

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
    <div
      className={clsx(
        "fixed inset-0 bg-darken-6 flex items-center justify-center z-50 focus:outline-none",
        `p-${padding}`
      )}
    >
      <div
        className={clsx(
          "rounded-lg shadow-md w-full focus:outline-none",
          size === "m" && "max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl",
          size === "l" && "max-w-screen"
        )}
        onClick={(e) => e.stopPropagation()}
        ref={modalRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
      >
        <BackgroundTexture className="rounded-lg border-1 border-neutral-700">
          <div className="max-h-screen">
            <div className="pt-2 px-2 flex items-center justify-between pb-2 bg-darken-4 rounded-t-lg">
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
            <SectionDivider color="gradient" className="mb-1" height={1} />
            <div
              className={clsx(
                "pb-10 overflow-y-auto max-h-[90vh]",
                `pt-${padding}`,
                `px-${paddingX}`
              )}
            >
              {children}
            </div>
          </div>
        </BackgroundTexture>
      </div>
    </div>,
    document.body
  );
};

export default Modal;
