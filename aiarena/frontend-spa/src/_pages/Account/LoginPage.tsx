import { useState } from "react";
import { graphql, useMutation } from "react-relay";
import { Link, useSearchParams } from "react-router";
import Form from "@/_components/_actions/Form";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import AccountInput from "./_components/AccountInput";
import { FormAlert } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { LoginPageMutation } from "./__generated__/LoginPageMutation.graphql";

export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [signIn, signingIn] = useMutation<LoginPageMutation>(graphql`
    mutation LoginPageMutation($input: PasswordSignInInput!) {
      passwordSignIn(input: $input) {
        redirectTo
        errors {
          field
          messages
        }
      }
    }
  `);
  const { backendErrors, onCompleted, onError } =
    useBackendErrors("passwordSignIn");
  const { byField, general } = splitAccountErrors(backendErrors, [
    "username",
    "password",
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    signIn({
      variables: {
        input: { username, password, nextUrl: searchParams.get("next") },
      },
      onCompleted: (response, errors) => {
        const redirectTo = response.passwordSignIn?.redirectTo;
        if (onCompleted(response, errors) && redirectTo) {
          // The backend validated `next` (or chose the default page), so just
          // go there. A full navigation, not client-side routing: signing in
          // rotates the CSRF token, and the next page may be server-rendered.
          window.location.assign(redirectTo);
        }
      },
      onError,
    });
  };

  return (
    <AccountCard
      title="Log in"
      footer={
        <>
          <Link to={reverseUrl("password_reset")}>Forgot password?</Link>
          <Link to={reverseUrl("registration_register")}>
            Create an account
          </Link>
        </>
      }
    >
      <FormAlert messages={general} />
      <Form
        handleSubmit={handleSubmit}
        loading={signingIn}
        submitTitle="Log in"
      >
        <AccountInput
          id="username"
          label="Username"
          value={username}
          onChange={setUsername}
          autoComplete="username"
          autoFocus
          errors={byField.username}
        />
        <AccountInput
          id="password"
          label="Password"
          type="password"
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
          errors={byField.password}
        />
      </Form>
    </AccountCard>
  );
}
