import { useState } from "react";
import { graphql, useMutation } from "react-relay";
import { Link, useParams } from "react-router";
import Form from "@/_components/_actions/Form";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import AccountInput from "./_components/AccountInput";
import { FormAlert, FormSuccess } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { PasswordResetConfirmPageMutation } from "./__generated__/PasswordResetConfirmPageMutation.graphql";

/** The page a password-reset email links to: choose a new password. */
export default function PasswordResetConfirmPage() {
  const { uidb64 = "", token = "" } = useParams<{
    uidb64: string;
    token: string;
  }>();
  const [newPassword1, setNewPassword1] = useState("");
  const [newPassword2, setNewPassword2] = useState("");
  const [done, setDone] = useState(false);

  const [resetPassword, resetting] =
    useMutation<PasswordResetConfirmPageMutation>(graphql`
      mutation PasswordResetConfirmPageMutation($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          errors {
            field
            messages
          }
        }
      }
    `);
  const { backendErrors, onCompleted, onError } =
    useBackendErrors("resetPassword");
  const { byField, general } = splitAccountErrors(backendErrors, [
    "newPassword1",
    "newPassword2",
  ]);
  // An invalid/expired link can't be fixed by retyping — point at a new one.
  const linkInvalid = (backendErrors.formErrors ?? []).some(
    (e) => e?.field === "token",
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    resetPassword({
      variables: { input: { uidb64, token, newPassword1, newPassword2 } },
      onCompleted: (...args) => setDone(onCompleted(...args)),
      onError,
    });
  };

  return (
    <AccountCard
      title="Choose a new password"
      footer={
        done ? undefined : (
          <Link to={reverseUrl("password_reset")}>Request a new reset link</Link>
        )
      }
    >
      {done ? (
        <FormSuccess>
          Your password has been changed.{" "}
          <Link to={reverseUrl("login")}>Log in</Link> with your new password.
        </FormSuccess>
      ) : (
        <>
          <FormAlert messages={general} />
          {!linkInvalid && (
            <Form
              handleSubmit={handleSubmit}
              loading={resetting}
              submitTitle="Set new password"
            >
              <AccountInput
                id="newPassword1"
                label="New password"
                type="password"
                value={newPassword1}
                onChange={setNewPassword1}
                autoComplete="new-password"
                autoFocus
                errors={byField.newPassword1}
              />
              <AccountInput
                id="newPassword2"
                label="Confirm new password"
                type="password"
                value={newPassword2}
                onChange={setNewPassword2}
                autoComplete="new-password"
                errors={byField.newPassword2}
              />
            </Form>
          )}
        </>
      )}
    </AccountCard>
  );
}
