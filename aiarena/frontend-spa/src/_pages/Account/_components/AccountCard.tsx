import { ReactNode } from "react";

interface AccountCardProps {
  title: string;
  intro?: ReactNode;
  children: ReactNode;
  /** Links at the bottom of the card, e.g. "Forgot password?" / "Register". */
  footer?: ReactNode;
}

/** The centered card every account page (login, register, reset…) sits in. */
export default function AccountCard({
  title,
  intro,
  children,
  footer,
}: AccountCardProps) {
  return (
    <div className="mx-auto mt-6 w-full max-w-md md:mt-12">
      <section className="rounded-xl border border-neutral-700 bg-neutral-900 p-6 shadow-lg shadow-black">
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
        {intro && <div className="mt-2 text-sm text-gray-300">{intro}</div>}
        <div className="mt-6">{children}</div>
        {footer && (
          <div className="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 border-t border-neutral-700 pt-4 text-sm">
            {footer}
          </div>
        )}
      </section>
    </div>
  );
}
