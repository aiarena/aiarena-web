import { useEffect, useRef, useState } from "react";
import { graphql, useMutation } from "react-relay";
import { Link, useParams } from "react-router";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import LoadingDots from "@/_components/_display/LoadingDots";
import AccountCard from "./_components/AccountCard";
import { FormAlert, FormSuccess } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { ActivateAccountPageMutation } from "./__generated__/ActivateAccountPageMutation.graphql";

/** The page an activation email links to: activates on arrival. */
export default function ActivateAccountPage() {
  const { activationKey = "" } = useParams<{ activationKey: string }>();
  const [activated, setActivated] = useState(false);
  const started = useRef(false);

  const [activate, activating] = useMutation<ActivateAccountPageMutation>(
    graphql`
      mutation ActivateAccountPageMutation($input: ActivateAccountInput!) {
        activateAccount(input: $input) {
          errors {
            field
            messages
          }
        }
      }
    `,
  );
  const { backendErrors, onCompleted, onError } =
    useBackendErrors("activateAccount");
  const { general } = splitAccountErrors(backendErrors, []);

  useEffect(() => {
    // A key only works once; StrictMode's double-mount would burn it on the
    // first call and show an error from the second.
    if (started.current) return;
    started.current = true;
    activate({
      variables: { input: { activationKey } },
      onCompleted: (...args) => setActivated(onCompleted(...args)),
      onError,
    });
  }, [activate, activationKey, onCompleted, onError]);

  return (
    <AccountCard
      title="Activate your account"
      footer={
        !activated &&
        !activating && (
          <Link to={reverseUrl("registration_resend_activation")}>
            Send a new activation email
          </Link>
        )
      }
    >
      {activating || (!activated && general.length === 0) ? (
        <LoadingDots />
      ) : activated ? (
        <FormSuccess>
          Your account is active.{" "}
          <Link to={reverseUrl("login")}>Log in</Link> to get started.
        </FormSuccess>
      ) : (
        <FormAlert messages={general} />
      )}
    </AccountCard>
  );
}
