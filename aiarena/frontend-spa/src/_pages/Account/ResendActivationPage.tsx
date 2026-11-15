import { useState } from "react";
import { graphql, useMutation } from "react-relay";
import { Link } from "react-router";
import Form from "@/_components/_actions/Form";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import AccountInput from "./_components/AccountInput";
import { EmailDelayNote, FormAlert, FormSuccess } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { ResendActivationPageMutation } from "./__generated__/ResendActivationPageMutation.graphql";

export default function ResendActivationPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  const [resend, resending] = useMutation<ResendActivationPageMutation>(graphql`
    mutation ResendActivationPageMutation(
      $input: ResendActivationEmailInput!
    ) {
      resendActivationEmail(input: $input) {
        errors {
          field
          messages
        }
      }
    }
  `);
  const { backendErrors, onCompleted, onError } = useBackendErrors(
    "resendActivationEmail",
  );
  const { byField, general } = splitAccountErrors(backendErrors, ["email"]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    resend({
      variables: { input: { email } },
      onCompleted: (...args) => setSent(onCompleted(...args)),
      onError,
    });
  };

  return (
    <AccountCard
      title="Resend activation email"
      intro="Enter the email you registered with and we'll send a fresh activation link."
      footer={<Link to={reverseUrl("login")}>Back to log in</Link>}
    >
      {sent ? (
        // Deliberately the same message whether or not the address has a
        // pending account, so this form can't be used to probe for accounts.
        <FormSuccess>
          If <strong>{email}</strong> belongs to an account that isn't
          activated yet, a new activation link is on its way.
          <EmailDelayNote />
        </FormSuccess>
      ) : (
        <>
          <FormAlert messages={general} />
          <Form
            handleSubmit={handleSubmit}
            loading={resending}
            submitTitle="Send activation email"
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
