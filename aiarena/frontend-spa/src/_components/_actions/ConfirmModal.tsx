import { ReactNode } from "react";

import Modal from "./Modal";
import SquareButton from "./SquareButton";

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  /** What will happen, so the user knows what they're agreeing to. */
  children: ReactNode;
  confirmText: string;
}

/** "Are you sure?" dialog for destructive actions: Cancel, or a red button
 * that does the thing. */
export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  children,
  confirmText,
}: ConfirmModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="text-gray-300">{children}</div>
      <div className="mt-6 flex flex-wrap justify-end gap-3">
        <SquareButton onClick={onClose} text="Cancel" textColor="dim" />
        <SquareButton
          onClick={() => {
            onClose();
            onConfirm();
          }}
          text={confirmText}
          color="red"
        />
      </div>
    </Modal>
  );
}
