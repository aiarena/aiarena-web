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
