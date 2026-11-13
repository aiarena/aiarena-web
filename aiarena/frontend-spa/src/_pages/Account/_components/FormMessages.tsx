/** The general (non-field) messages, shown above a form. */
export function FormAlert({ messages }: { messages: readonly string[] }) {
  if (messages.length === 0) return null;
  return (
    <div
      role="alert"
      className="mb-4 rounded-md border border-red-500/50 bg-red-500/10 px-3 py-2 text-sm text-red-300"
    >
      {messages.map((message) => (
        <p key={message}>{message}</p>
      ))}
    </div>
  );
}

/** Shown wherever we've just sent an email: emails go out from a background
 * queue, so they don't arrive the instant the page says "sent". */
export function EmailDelayNote() {
  return (
    <p className="mt-2 text-gray-300">
      We're sending the email now. It can take a few minutes to arrive -
      remember to also check your spam folder.
    </p>
  );
}

/** A success / info panel that replaces a form once it's done its job. */
export function FormSuccess({ children }: { children: React.ReactNode }) {
  return (
    <div
      role="status"
      className="rounded-md border border-customGreen/50 bg-customGreen/10 px-3 py-3 text-sm text-gray-100"
    >
      {children}
    </div>
  );
}
