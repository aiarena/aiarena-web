import re

from django.contrib.auth import get_user
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import pytest
from registration.models import RegistrationProfile

from aiarena.core.models import WebsiteUser
from aiarena.core.tests.base import GraphQLTest
from aiarena.core.utils import camel_case
from aiarena.graphql.account_mutations import UpdateAccountSettings
from aiarena.graphql.common import NOT_LOGGED_IN_MESSAGE


class TestPasswordSignIn(GraphQLTest):
    """The sign-in mutation is anonymous-allowed (allow_anonymous=True): the
    login-by-default gate must NOT block an unauthenticated caller, or nobody
    could ever sign in."""

    mutation_name = "passwordSignIn"
    # language=graphql
    mutation = """
        mutation ($input: PasswordSignInInput!) {
            passwordSignIn(input: $input) {
                errors {
                    messages
                    field
                }
            }
        }
    """

    def test_anonymous_can_sign_in_with_valid_credentials(self, user):
        """An anonymous caller reaches the auth logic (not blocked by the login
        floor) and ends up authenticated in the session."""
        self.mutate(
            expected_status=200,
            variables={"input": {"username": "billy", "password": "guest"}},
        )

        assert get_user(self.last_query_client).is_authenticated

    def test_wrong_password_returns_error_payload(self, user):
        """Bad credentials return a graceful error payload, not auth."""
        self.mutate(
            expected_status=200,
            expected_validation_errors={"__all__": ["Incorrect username or password"]},
            variables={"input": {"username": "billy", "password": "wrong"}},
        )

        assert not get_user(self.last_query_client).is_authenticated


class TestPasswordSignInRedirect(GraphQLTest):
    """After signing in, the client goes to `redirectTo`. The requested `nextUrl`
    is only honoured when it's a safe same-site URL; anything else falls back
    to the default page, so `?next=` can't be used as an open redirect."""

    mutation_name = "passwordSignIn"
    # language=graphql
    mutation = """
        mutation ($input: PasswordSignInInput!) {
            passwordSignIn(input: $input) {
                redirectTo
                errors {
                    messages
                    field
                }
            }
        }
    """

    def _redirect_to(self, next_url):
        variables = {"input": {"username": "billy", "password": "guest", "nextUrl": next_url}}
        return self.mutate(variables=variables)["passwordSignIn"]["redirectTo"]

    @pytest.mark.parametrize(
        "next_url",
        [
            "/dashboard/",
            "/bots/42/?tab=matches",
            # Same host as the request (the test client's), so allowed.
            "http://testserver/dashboard/",
        ],
    )
    def test_safe_next_url_is_followed(self, user, next_url):
        assert self._redirect_to(next_url) == next_url

    @pytest.mark.parametrize(
        "next_url",
        [
            "//evil.com",
            "/\\evil.com",
            "/\t/evil.com",
            "/\n/evil.com",
            "https://evil.com/",
            "javascript:alert(1)",
        ],
    )
    def test_unsafe_next_url_falls_back_to_default(self, user, next_url):
        assert self._redirect_to(next_url) == reverse("home")

    @pytest.mark.parametrize("next_url", [None, ""])
    def test_missing_next_url_goes_to_default(self, user, next_url):
        assert self._redirect_to(next_url) == reverse("home")

    def test_failed_sign_in_has_no_redirect(self, user):
        response = self.mutate(
            variables={"input": {"username": "billy", "password": "wrong", "nextUrl": "/dashboard/"}},
            expected_validation_errors={"__all__": ["Incorrect username or password"]},
        )
        assert response["passwordSignIn"]["redirectTo"] is None


class TestSignOut(GraphQLTest):
    """Sign-out is anonymous-allowed: an already-anonymous caller gets a graceful
    error payload rather than being blocked by the login floor."""

    mutation_name = "signOut"
    # language=graphql
    mutation = """
        mutation {
            signOut {
                errors {
                    messages
                    field
                }
            }
        }
    """

    def test_signed_in_user_is_signed_out(self, user):
        self.mutate(login_user=user, expected_status=200)

        assert not get_user(self.last_query_client).is_authenticated

    def test_anonymous_is_denied(self, db):
        """Sign-out requires auth like any other mutation. Denying a logged-out
        caller is the honest signal (e.g. a frontend with stale auth state learns
        the session is already gone) — better than a no-op that reports success."""
        self.mutate(
            expected_status=200,
            expected_errors_like=[NOT_LOGGED_IN_MESSAGE],
        )


ERRORS = """
    errors {
        messages
        field
    }
"""


@pytest.fixture
def pending_registration(db):
    """A registered-but-not-yet-activated account, as left by the Register mutation."""
    new_user = WebsiteUser(username="newbie", email="newbie@example.com")
    new_user.set_password("a-Strong-pass-123")
    user = RegistrationProfile.objects.create_inactive_user(site=None, new_user=new_user, send_email=False)
    return user


class TestRegister(GraphQLTest):
    mutation_name = "register"
    # language=graphql
    mutation = f"""
        mutation ($input: RegisterInput!) {{
            register(input: $input) {{ {ERRORS} }}
        }}
    """

    def _input(self, **overrides):
        return {
            "input": {
                "username": "newbie",
                "email": "newbie@example.com",
                "password1": "a-Strong-pass-123",
                "password2": "a-Strong-pass-123",
                **overrides,
            }
        }

    def test_anonymous_registers_inactive_account_and_gets_activation_email(
        self, db, mailoutbox, django_capture_on_commit_callbacks
    ):
        # registration-redux sends the email on transaction commit.
        with django_capture_on_commit_callbacks(execute=True):
            self.mutate(variables=self._input())

        user = WebsiteUser.objects.get(username="newbie")
        assert not user.is_active
        profile = RegistrationProfile.objects.get(user=user)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ["newbie@example.com"]
        # The email links to the SPA activation page for this account's key.
        assert reverse("registration_activate", args=[profile.activation_key]) in mailoutbox[0].body

    def test_mismatched_passwords_are_rejected(self, db, mailoutbox):
        self.mutate(
            variables=self._input(password2="something-else-456"),
            expected_validation_errors={"password2": ["The two password fields didn’t match."]},
        )
        assert not WebsiteUser.objects.filter(username="newbie").exists()
        assert mailoutbox == []

    def test_taken_username_is_rejected(self, user, mailoutbox):
        self.mutate(
            variables=self._input(username=user.username),
            expected_validation_errors={"username": ["A user with that username already exists."]},
        )
        assert mailoutbox == []

    def test_closed_registration_is_rejected(self, db, settings):
        settings.REGISTRATION_OPEN = False
        self.mutate(
            variables=self._input(),
            expected_validation_errors={"__all__": ["Registration is currently closed."]},
        )
        assert not WebsiteUser.objects.filter(username="newbie").exists()


class TestActivateAccount(GraphQLTest):
    mutation_name = "activateAccount"
    # language=graphql
    mutation = f"""
        mutation ($input: ActivateAccountInput!) {{
            activateAccount(input: $input) {{ {ERRORS} }}
        }}
    """

    def test_valid_key_activates_the_account(self, pending_registration):
        key = RegistrationProfile.objects.get(user=pending_registration).activation_key
        self.mutate(variables={"input": {"activationKey": key}})

        pending_registration.refresh_from_db()
        assert pending_registration.is_active

    def test_key_cannot_be_used_twice(self, pending_registration):
        key = RegistrationProfile.objects.get(user=pending_registration).activation_key
        self.mutate(variables={"input": {"activationKey": key}})
        self.mutate(
            variables={"input": {"activationKey": key}},
            expected_validation_errors={
                "activationKey": ["This activation link is invalid, has expired, or was already used."]
            },
        )

    def test_unknown_key_is_rejected(self, db):
        self.mutate(
            variables={"input": {"activationKey": "0" * 64}},
            expected_validation_errors={
                "activationKey": ["This activation link is invalid, has expired, or was already used."]
            },
        )


class TestResendActivationEmail(GraphQLTest):
    mutation_name = "resendActivationEmail"
    # language=graphql
    mutation = f"""
        mutation ($input: ResendActivationEmailInput!) {{
            resendActivationEmail(input: $input) {{ {ERRORS} }}
        }}
    """

    def test_resends_to_a_pending_account(self, pending_registration, mailoutbox):
        self.mutate(variables={"input": {"email": pending_registration.email}})
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [pending_registration.email]

    def test_unknown_address_reports_success_without_sending(self, db, mailoutbox):
        """Same response as for a real address, so it can't be used to probe accounts."""
        self.mutate(variables={"input": {"email": "nobody@example.com"}})
        assert mailoutbox == []


class TestRequestPasswordReset(GraphQLTest):
    mutation_name = "requestPasswordReset"
    # language=graphql
    mutation = f"""
        mutation ($input: RequestPasswordResetInput!) {{
            requestPasswordReset(input: $input) {{ {ERRORS} }}
        }}
    """

    def test_emails_a_working_reset_link(self, user, mailoutbox):
        self.mutate(variables={"input": {"email": user.email}})

        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]
        uidb64, token = re.search(r"/accounts/reset/([^/]+)/([^/]+)/", mailoutbox[0].body).groups()
        assert uidb64 == urlsafe_base64_encode(force_bytes(user.pk))
        assert default_token_generator.check_token(user, token)

    def test_unknown_address_reports_success_without_sending(self, db, mailoutbox):
        """Same response as for a real address, so it can't be used to probe accounts."""
        self.mutate(variables={"input": {"email": "nobody@example.com"}})
        assert mailoutbox == []


class TestResetPassword(GraphQLTest):
    mutation_name = "resetPassword"
    # language=graphql
    mutation = f"""
        mutation ($input: ResetPasswordInput!) {{
            resetPassword(input: $input) {{ {ERRORS} }}
        }}
    """

    def _input(self, user, token=None, password2="a-New-pass-789"):
        return {
            "input": {
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": token or default_token_generator.make_token(user),
                "newPassword1": "a-New-pass-789",
                "newPassword2": password2,
            }
        }

    def test_valid_link_sets_the_new_password(self, user):
        self.mutate(variables=self._input(user))
        user.refresh_from_db()
        assert user.check_password("a-New-pass-789")

    def test_link_cannot_be_reused(self, user):
        variables = self._input(user)
        self.mutate(variables=variables)
        self.mutate(
            variables=variables,
            expected_validation_errors={"token": ["This password reset link is invalid or has expired."]},
        )

    def test_bad_token_is_rejected(self, user):
        self.mutate(
            variables=self._input(user, token="bad-token"),
            expected_validation_errors={"token": ["This password reset link is invalid or has expired."]},
        )
        user.refresh_from_db()
        assert user.check_password("guest")

    def test_mismatched_passwords_are_rejected(self, user):
        self.mutate(
            variables=self._input(user, password2="different-pass-000"),
            expected_validation_errors={"newPassword2": ["The two password fields didn’t match."]},
        )
        user.refresh_from_db()
        assert user.check_password("guest")


class TestChangePassword(GraphQLTest):
    mutation_name = "changePassword"
    # language=graphql
    mutation = f"""
        mutation ($input: ChangePasswordInput!) {{
            changePassword(input: $input) {{ {ERRORS} }}
        }}
    """

    def _input(self, old_password="guest"):
        return {
            "input": {
                "oldPassword": old_password,
                "newPassword1": "a-New-pass-789",
                "newPassword2": "a-New-pass-789",
            }
        }

    def test_signed_in_user_changes_password_and_stays_signed_in(self, user):
        self.mutate(login_user=user, variables=self._input())

        user.refresh_from_db()
        assert user.check_password("a-New-pass-789")
        assert get_user(self.last_query_client).is_authenticated

    def test_wrong_old_password_is_rejected(self, user):
        self.mutate(
            login_user=user,
            variables=self._input(old_password="wrong"),
            expected_validation_errors={
                "oldPassword": ["Your old password was entered incorrectly. Please enter it again."]
            },
        )
        user.refresh_from_db()
        assert user.check_password("guest")

    def test_anonymous_is_denied(self, db):
        self.mutate(variables=self._input(), expected_errors_like=[NOT_LOGGED_IN_MESSAGE])


class TestUpdateAccountSettings(GraphQLTest):
    mutation_name = "updateAccountSettings"
    # language=graphql
    mutation = f"""
        mutation ($input: UpdateAccountSettingsInput!) {{
            updateAccountSettings(input: $input) {{
                viewer {{ receiveEmailComms }}
                {ERRORS}
            }}
        }}
    """

    def test_user_can_opt_out_and_back_in(self, user):
        assert user.receive_email_comms

        response = self.mutate(login_user=user, variables={"input": {"receiveEmailComms": False}})
        user.refresh_from_db()
        assert not user.receive_email_comms
        assert response["updateAccountSettings"]["viewer"]["receiveEmailComms"] is False

        self.mutate(login_user=user, variables={"input": {"receiveEmailComms": True}})
        user.refresh_from_db()
        assert user.receive_email_comms

    def test_omitted_field_is_left_unchanged(self, user):
        user.receive_email_comms = False
        user.save()

        self.mutate(login_user=user, variables={"input": {}})
        user.refresh_from_db()
        assert not user.receive_email_comms

    def test_only_affects_the_caller(self, user, other_user):
        self.mutate(login_user=user, variables={"input": {"receiveEmailComms": False}})
        other_user.refresh_from_db()
        assert other_user.receive_email_comms

    def test_input_exposes_exactly_the_editable_fields(self, db):
        """The public input type and the mutation's allowlist must match: adding
        an input field without allowlisting it (or vice versa) fails here, so
        widening what users can change is always a deliberate, reviewed edit."""
        data = self.query(
            query="""
                { __type(name: "UpdateAccountSettingsInput") { inputFields { name } } }
            """
        )
        exposed = {f["name"] for f in data["__type"]["inputFields"]}

        assert exposed == {camel_case(f) for f in UpdateAccountSettings.EDITABLE_FIELDS}
        assert exposed == {"receiveEmailComms"}

    @pytest.mark.parametrize(
        "field, value",
        [
            ("patreonLevel", "diamond"),
            ("email", "attacker@example.com"),
            ("username", "hijacked"),
            ("isStaff", True),
            ("isSuperuser", True),
            ("syncPatreonStatus", False),
        ],
    )
    def test_non_editable_fields_are_rejected_and_unchanged(self, user, field, value):
        """Sending any field outside the allowlist is rejected by schema
        validation, and nothing on the user changes, including the editable
        field sent alongside it."""
        before = {
            f: getattr(user, f)
            for f in [
                "patreon_level",
                "email",
                "username",
                "is_staff",
                "is_superuser",
                "sync_patreon_status",
                "receive_email_comms",
            ]
        }

        self.mutate(
            login_user=user,
            variables={"input": {"receiveEmailComms": False, field: value}},
            expected_status=400,
            expected_errors_like=[f"Field '{field}' is not defined by type 'UpdateAccountSettingsInput'"],
        )

        user.refresh_from_db()
        assert {f: getattr(user, f) for f in before} == before

    def test_anonymous_is_denied(self, user):
        self.mutate(
            variables={"input": {"receiveEmailComms": False}},
            expected_errors_like=[NOT_LOGGED_IN_MESSAGE],
        )
        user.refresh_from_db()
        assert user.receive_email_comms
