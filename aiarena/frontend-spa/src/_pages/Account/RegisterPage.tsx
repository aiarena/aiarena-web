import { useState } from "react";
import { graphql, useMutation } from "react-relay";
import { Link, useNavigate } from "react-router";
import Form from "@/_components/_actions/Form";
import useBackendErrors from "@/_lib/useBackendErrors";
import { reverseUrl } from "@/_lib/reverseUrl";
import AccountCard from "./_components/AccountCard";
import AccountInput from "./_components/AccountInput";
import { FormAlert } from "./_components/FormMessages";
import { splitAccountErrors } from "./_components/splitAccountErrors";
import { RegisterPageMutation } from "./__generated__/RegisterPageMutation.graphql";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");

  const [register, registering] = useMutation<RegisterPageMutation>(graphql`
    mutation RegisterPageMutation($input: RegisterInput!) {
      register(input: $input) {
        errors {
          field
          messages
        }
      }
    }
  `);
  const { backendErrors, onCompleted, onError } = useBackendErrors("register");
  const { byField, general } = splitAccountErrors(backendErrors, [
    "username",
    "email",
    "password1",
    "password2",
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    register({
      variables: { input: { username, email, password1, password2 } },
      onCompleted: (...args) => {
        if (onCompleted(...args)) {
          navigate(reverseUrl("registration_complete"), { state: { email } });
        }
      },
      onError,
    });
  };

  return (
    <AccountCard
      title="Create an account"
      intro="We'll email you a link to activate your account."
      footer={
        <>
          <span className="text-gray-400">
            Already registered? <Link to={reverseUrl("login")}>Log in</Link>
          </span>
          <Link to={reverseUrl("registration_resend_activation")}>
            Resend activation email
          </Link>
        </>
      }
    >
      <FormAlert messages={general} />
      <Form
        handleSubmit={handleSubmit}
        loading={registering}
        submitTitle="Register"
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
          id="email"
          label="Email"
          type="email"
          value={email}
          onChange={setEmail}
          autoComplete="email"
          errors={byField.email}
        />
        <AccountInput
          id="password1"
          label="Password"
          type="password"
          value={password1}
          onChange={setPassword1}
          autoComplete="new-password"
          errors={byField.password1}
        />
        <AccountInput
          id="password2"
          label="Confirm password"
          type="password"
          value={password2}
          onChange={setPassword2}
          autoComplete="new-password"
          errors={byField.password2}
        />
      </Form>
    </AccountCard>
  );
}
