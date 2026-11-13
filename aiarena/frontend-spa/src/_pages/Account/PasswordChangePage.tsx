import { useState } from "react";
import { graphql, useLazyLoadQuery, useMutation } from "react-relay";
import { Link } from "react-router";
import Form from "@/_components/_actions/Form";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import AccountInput from "./_components/AccountInput";
import { FormAlert, FormSuccess } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { PasswordChangePageQuery } from "./__generated__/PasswordChangePageQuery.graphql";
import { PasswordChangePageMutation } from "./__generated__/PasswordChangePageMutation.graphql";

/** Change the signed-in user's password. */
export default function PasswordChangePage() {
  const data = useLazyLoadQuery<PasswordChangePageQuery>(
    graphql`
      query PasswordChangePageQuery {
        viewer {
          user {
            id
          }
        }
      }
    `,
    {},
  );
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword1, setNewPassword1] = useState("");
  const [newPassword2, setNewPassword2] = useState("");
  const [done, setDone] = useState(false);

  const [changePassword, changing] = useMutation<PasswordChangePageMutation>(
    graphql`
      mutation PasswordChangePageMutation($input: ChangePasswordInput!) {
        changePassword(input: $input) {
          errors {
            field
            messages
          }
        }
      }
    `,
  );
  const { backendErrors, onCompleted, onError } =
    useBackendErrors("changePassword");
  const { byField, general } = splitAccountErrors(backendErrors, [
    "oldPassword",
    "newPassword1",
    "newPassword2",
  ]);

  if (!data.viewer?.user) {
    window.location.replace(
      `${reverseUrl("login")}?next=${encodeURIComponent(window.location.pathname)}`,
    );
    return null;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    changePassword({
      variables: { input: { oldPassword, newPassword1, newPassword2 } },
      onCompleted: (...args) => setDone(onCompleted(...args)),
      onError,
    });
  };

  return (
    <AccountCard
      title="Change password"
      footer={
        <Link to={reverseUrl("dashboard_profile")}>Back to your profile</Link>
      }
    >
      {done ? (
        <FormSuccess>Your password has been changed.</FormSuccess>
      ) : (
        <>
          <FormAlert messages={general} />
          <Form
            handleSubmit={handleSubmit}
            loading={changing}
            submitTitle="Change password"
          >
            <AccountInput
              id="oldPassword"
              label="Current password"
              type="password"
              value={oldPassword}
              onChange={setOldPassword}
              autoComplete="current-password"
              autoFocus
              errors={byField.oldPassword}
            />
            <AccountInput
              id="newPassword1"
              label="New password"
              type="password"
              value={newPassword1}
              onChange={setNewPassword1}
              autoComplete="new-password"
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
        </>
      )}
    </AccountCard>
  );
}
