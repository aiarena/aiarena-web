import { Link, useLocation } from "react-router";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import { EmailDelayNote, FormSuccess } from "./_components/FormMessages";

export default function RegistrationCompletePage() {
  // Set by the register page; absent on a hard refresh, so fall back to generic copy.
  const email = (useLocation().state as { email?: string } | null)?.email;

  return (
    <AccountCard
      title="Check your email"
      footer={
        <Link to={reverseUrl("registration_resend_activation")}>
          Didn't get it? Resend the activation email
        </Link>
      }
    >
      <FormSuccess>
        We've sent an activation link to{" "}
        {email ? <strong>{email}</strong> : "your email address"}. Open it to
        activate your account, then log in.
        <EmailDelayNote />
      </FormSuccess>
    </AccountCard>
  );
}
