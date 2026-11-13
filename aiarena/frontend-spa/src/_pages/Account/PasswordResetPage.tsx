import { useState } from "react";
import { graphql, useMutation } from "react-relay";
import { Link } from "react-router";
import Form from "@/_components/_actions/Form";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import AccountInput from "./_components/AccountInput";
import { FormAlert, FormSuccess } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { PasswordResetPageMutation } from "./__generated__/PasswordResetPageMutation.graphql";

/** "Forgot password": request a reset link by email. */
export default function PasswordResetPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  const [requestReset, requesting] = useMutation<PasswordResetPageMutation>(
    graphql`
      mutation PasswordResetPageMutation($input: RequestPasswordResetInput!) {
        requestPasswordReset(input: $input) {
          errors {
            field
            messages
          }
        }
      }
    `,
  );
  const { backendErrors, onCompleted, onError } = useBackendErrors(
    "requestPasswordReset",
  );
  const { byField, general } = splitAccountErrors(backendErrors, ["email"]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    requestReset({
      variables: { input: { email } },
      onCompleted: (...args) => setSent(onCompleted(...args)),
      onError,
    });
  };

  return (
    <AccountCard
      title="Reset your password"
      intro="Enter your account's email and we'll send you a link to choose a new password."
      footer={<Link to={reverseUrl("login")}>Back to log in</Link>}
    >
      {sent ? (
        // Deliberately the same message whether or not the address is
        // registered, so this form can't be used to probe for accounts.
        <FormSuccess>
          If <strong>{email}</strong> belongs to an account, a password reset
          link is on its way. It can be used once.
        </FormSuccess>
      ) : (
        <>
          <FormAlert messages={general} />
          <Form
            handleSubmit={handleSubmit}
            loading={requesting}
            submitTitle="Send reset link"
          >
            <AccountInput
              id="email"
              label="Email"
              type="email"
              value={email}
              onChange={setEmail}
              autoComplete="email"
              autoFocus
              errors={byField.email}
            />
          </Form>
        </>
      )}
    </AccountCard>
  );
}
