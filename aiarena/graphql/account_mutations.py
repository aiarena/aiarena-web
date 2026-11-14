"""Account mutations: sign in/out, registration + activation, password reset and change,
and unlinking Discord.

All but sign-out and password change are anonymous by definition — see the
"Login is required by default" section of this package's CLAUDE.md.

Each mutation delegates validation to the same Django forms the old template
views used (registration-redux's registration form, Django's password forms), so
password validators, uniqueness checks and email/token handling stay identical.
"""

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import resolve_url
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode

import graphene
from graphene_django.types import ErrorType
from registration import signals
from registration.models import RegistrationProfile

from aiarena.core.models import User
from aiarena.core.utils import camel_case
from aiarena.frontend.forms import WebsiteUserRegistrationForm
from aiarena.graphql.common import BaseMutation, CleanedInputMutation, CleanedInputType


def _error(message: str, field: str = "__all__") -> list[ErrorType]:
    return [ErrorType(field=field, messages=[message])]


def _form_errors(form) -> list[ErrorType]:
    """A Django form's errors as GraphQL errors, with camelCase field names like
    every other mutation's (``new_password1`` -> ``newPassword1``)."""
    return [
        ErrorType(field=field if field == "__all__" else camel_case(field), messages=list(messages))
        for field, messages in form.errors.items()
    ]


# =============================================================================
# Sign in / out
# =============================================================================


class PasswordSignInInput(CleanedInputType):
    username = graphene.String()
    password = graphene.String()
    # Where the caller wants to go after signing in (the login page's `?next=`).
    next_url = graphene.String()


def _safe_redirect_url(request, next_url: str | None) -> str:
    """``next_url`` if it's safe to send the user to, else the default
    post-login page. Same check as Django's LoginView, so `?next=` can never
    send a freshly signed-in user to another site (open redirect)."""
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return resolve_url(settings.LOGIN_REDIRECT_URL)


class PasswordSignIn(CleanedInputMutation):
    # Computed by the server, not an object the client could fetch: the
    # frontend navigates here unconditionally after a successful sign-in.
    redirect_to = graphene.String()

    class Meta:
        input_class = PasswordSignInInput
        # Anonymous by necessity: the caller is signing in, so they aren't
        # authenticated yet at entry.
        allow_anonymous = True

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        if user := authenticate(
            username=input_object.username,
            password=input_object.password,
        ):
            login(request=info.context, user=user)
        else:
            return cls(errors=_error("Incorrect username or password"))

        return cls(errors=[], redirect_to=_safe_redirect_url(info.context, input_object.next_url))


class SignOut(BaseMutation):
    def mutate(self, info: graphene.ResolveInfo) -> "SignOut":
        logout(request=info.context)
        return SignOut(errors=[])


# =============================================================================
# Registration + activation (django-registration-redux, default backend)
# =============================================================================


class RegisterInput(CleanedInputType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password1 = graphene.String(required=True)
    password2 = graphene.String(required=True)


class Register(CleanedInputMutation):
    """Create an inactive account and email its activation link.

    Mirrors registration-redux's ``RegistrationView.register`` so the activation
    key, email and ``user_registered`` signal are exactly what the old view did.
    """

    class Meta:
        input_class = RegisterInput
        # Anonymous by definition: you register because you have no account.
        allow_anonymous = True

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        if not getattr(settings, "REGISTRATION_OPEN", True):
            return cls(errors=_error("Registration is currently closed."))

        form = WebsiteUserRegistrationForm(
            data={
                "username": input_object.username,
                "email": input_object.email,
                "password1": input_object.password1,
                "password2": input_object.password2,
            }
        )
        if not form.is_valid():
            return cls(errors=_form_errors(form))

        request = info.context
        new_user = RegistrationProfile.objects.create_inactive_user(
            new_user=form.save(commit=False),
            site=get_current_site(request),
            send_email=getattr(settings, "SEND_ACTIVATION_EMAIL", True),
            request=request,
        )
        signals.user_registered.send(sender=cls, user=new_user, request=request)
        return cls(errors=[])


class ActivateAccountInput(CleanedInputType):
    activation_key = graphene.String(required=True)


class ActivateAccount(CleanedInputMutation):
    class Meta:
        input_class = ActivateAccountInput
        # Anonymous by definition: the account can't sign in until it's activated.
        allow_anonymous = True

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        request = info.context
        user, activated = RegistrationProfile.objects.activate_user(
            input_object.activation_key, get_current_site(request)
        )
        if not activated:
            return cls(
                errors=_error(
                    "This activation link is invalid, has expired, or was already used.",
                    field="activationKey",
                )
            )

        signals.user_activated.send(sender=cls, user=user, request=request)
        return cls(errors=[])


class ResendActivationEmailInput(CleanedInputType):
    email = graphene.String(required=True)


class ResendActivationEmail(CleanedInputMutation):
    """Resend the activation link. Always reports success, so the response
    doesn't reveal whether an address is registered."""

    class Meta:
        input_class = ResendActivationEmailInput
        # Anonymous by definition: the account isn't activated, so can't sign in.
        allow_anonymous = True

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        request = info.context
        RegistrationProfile.objects.resend_activation_mail(input_object.email, get_current_site(request), request)
        return cls(errors=[])


# =============================================================================
# Password reset (forgot password) and change
# =============================================================================


class RequestPasswordResetInput(CleanedInputType):
    email = graphene.String(required=True)


class RequestPasswordReset(CleanedInputMutation):
    """Email a password-reset link. Always reports success (for a well-formed
    address), so the response doesn't reveal whether an address is registered."""

    class Meta:
        input_class = RequestPasswordResetInput
        # Anonymous by definition: the user has forgotten their password.
        allow_anonymous = True

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        form = PasswordResetForm(data={"email": input_object.email})
        if not form.is_valid():
            return cls(errors=_form_errors(form))

        request = info.context
        # Same arguments Django's PasswordResetView passes.
        form.save(
            request=request,
            use_https=request.is_secure(),
            token_generator=default_token_generator,
            email_template_name="registration/password_reset_email.html",
        )
        return cls(errors=[])


class ResetPasswordInput(CleanedInputType):
    uidb64 = graphene.String(required=True)
    token = graphene.String(required=True)
    new_password1 = graphene.String(required=True)
    new_password2 = graphene.String(required=True)


class ResetPassword(CleanedInputMutation):
    """Set a new password from the uid/token in a reset email link."""

    class Meta:
        input_class = ResetPasswordInput
        # Anonymous by definition: the user can't sign in without the new password.
        allow_anonymous = True

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(input_object.uidb64)))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, input_object.token):
            return cls(errors=_error("This password reset link is invalid or has expired.", field="token"))

        form = SetPasswordForm(
            user,
            data={
                "new_password1": input_object.new_password1,
                "new_password2": input_object.new_password2,
            },
        )
        if not form.is_valid():
            return cls(errors=_form_errors(form))

        form.save()
        return cls(errors=[])


class ChangePasswordInput(CleanedInputType):
    old_password = graphene.String(required=True)
    new_password1 = graphene.String(required=True)
    new_password2 = graphene.String(required=True)


class ChangePassword(CleanedInputMutation):
    """Change the signed-in user's password (requires login, like any mutation)."""

    class Meta:
        input_class = ChangePasswordInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        request = info.context
        form = PasswordChangeForm(
            request.user,
            data={
                "old_password": input_object.old_password,
                "new_password1": input_object.new_password1,
                "new_password2": input_object.new_password2,
            },
        )
        if not form.is_valid():
            return cls(errors=_form_errors(form))

        form.save()
        # Keep the current session signed in after the password change.
        update_session_auth_hash(request, form.user)
        return cls(errors=[])


# =============================================================================
# Account settings
# =============================================================================


class UpdateAccountSettingsInput(CleanedInputType):
    # Every field here must also be listed in UpdateAccountSettings.EDITABLE_FIELDS
    # (a test enforces the two match).
    receive_email_comms = graphene.Boolean()


class UpdateAccountSettings(CleanedInputMutation):
    """Update the signed-in user's own account preferences. Acts only on the
    caller, so there is no object to authorize beyond login-by-default.

    Only the fields in ``EDITABLE_FIELDS`` can ever be written. Everything else
    on the user (email, Patreon level, staff flags, ...) is owned by other flows
    and must not be settable from here.
    """

    EDITABLE_FIELDS = ("receive_email_comms",)

    class Meta:
        input_class = UpdateAccountSettingsInput

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        user = info.context.user
        update_fields = []
        for field in cls.EDITABLE_FIELDS:
            value = getattr(input_object, field, None)
            if value is not None:
                setattr(user, field, value)
                update_fields.append(field)
        if update_fields:
            user.save(update_fields=update_fields)
        return cls(errors=[], viewer=user)


# =============================================================================
# Discord
# =============================================================================


class UnlinkDiscord(BaseMutation):
    """The SPA's equivalent of UnlinkDiscordView: delete the caller's Discord binding."""

    def mutate(self, info: graphene.ResolveInfo) -> "UnlinkDiscord":
        user = info.context.user
        user.discord_user.delete()
        # `viewer` resolves to this same user instance, which still caches the
        # deleted binding; reload it so `linkedDiscord` reads back as false.
        user.refresh_from_db()
        return UnlinkDiscord(errors=[])
