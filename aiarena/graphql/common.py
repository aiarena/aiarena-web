import functools
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

import graphene
from graphene import ID, InputObjectType
from graphene.types.inputobjecttype import InputObjectTypeOptions
from graphene.types.mutation import MutationOptions
from graphene.utils.get_unbound_function import get_unbound_function
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import _set_errors_flag_to_context
from graphene_django.types import ErrorType
from graphql import GraphQLError
from graphql.language.ast import StringValueNode
from graphql_relay import from_global_id

from aiarena.core import permissions
from aiarena.core.utils import camel_case


class CountingConnection(graphene.relay.Connection):
    """
    This adds totalCount to the connection.

    Borrowed from: https://github.com/graphql-python/graphene-django/issues/320
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, node=None, name=None, **options):
        result = super().__init_subclass_with_meta__(node=node, name=name, **options)
        cls._meta.fields["total_count"] = graphene.Field(
            type_=graphene.Int,
            name="totalCount",
            description="Number of items in the queryset.",
            required=True,
            resolver=cls.resolve_total_count,
        )
        return result

    def resolve_total_count(self, *_) -> int:
        if isinstance(self.iterable, QuerySet):
            return self.iterable.count()

        return len(self.iterable)


class DjangoObjectTypeWithUID(DjangoObjectType):
    database_id = graphene.Int(required=True, description="The underlying database primary key, for display purposes")

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        interfaces=(),
        **options,
    ):
        if not interfaces:
            interfaces = ()
        interfaces += (graphene.relay.Node,)
        super().__init_subclass_with_meta__(
            interfaces=interfaces,
            **options,
        )

    @staticmethod
    def resolve_database_id(root, info, **args):
        return root.id

    class Meta:
        abstract = True


class BaseMutation(graphene.Mutation):
    """Base class for every mutation in the schema.

    Login is required **by default**: the caller must be authenticated unless the
    mutation explicitly opts out with ``allow_anonymous = True`` in its ``Meta``.
    This is secure-by-default — anonymous access is a visible, greppable opt-in
    (used by auth-entry mutations like sign-in) rather than something each
    mutation has to remember to guard against.

    The check is injected by wrapping the subclass's ``mutate`` resolver, so it
    applies uniformly whether the subclass defines ``mutate(self, info)`` (a
    plain mutation) or inherits the input pipeline from ``CleanedInputMutation``.
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, allow_anonymous=False, resolver=None, **options):
        # Wrap the subclass's `mutate` with the login check BEFORE delegating to
        # graphene, which reads `mutate` to build the (then-frozen) resolver. We
        # can't reassign `_meta.resolver` afterwards — graphene freezes _meta.
        if not allow_anonymous:
            mutate = resolver or getattr(cls, "mutate", None)
            assert mutate, "All mutations must define a mutate method"
            resolver = cls._wrap_resolver_with_login(get_unbound_function(mutate))

        super().__init_subclass_with_meta__(resolver=resolver, **options)

    @staticmethod
    def _wrap_resolver_with_login(resolver):
        @functools.wraps(resolver)
        def wrapper(root, info, **kwargs):
            if not info.context.user.is_authenticated:
                raise AccessDenied(NOT_LOGGED_IN_MESSAGE)
            return resolver(root, info, **kwargs)

        return wrapper


class CleanedInputMutation(BaseMutation):
    class Meta:
        abstract = True

    errors = graphene.List(graphene.NonNull(ErrorType), required=True)
    node = graphene.relay.Node.Field()
    viewer = graphene.Field("aiarena.graphql.Viewer")

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        _meta=None,
        input_class=None,
        input_name="input",
        arguments=None,
        allow_anonymous=False,
        **options,
    ):
        if not _meta:
            _meta = MutationOptions(cls)

        _meta.input_name = input_name

        assert not arguments, "Can't specify any arguments"
        arguments = OrderedDict({input_name: input_class(required=True)})

        super().__init_subclass_with_meta__(
            allow_anonymous=allow_anonymous,
            output=None,
            arguments=arguments,
            _meta=_meta,
            **options,
        )

    @classmethod
    def clean_fields(
        cls,
        input_object: InputObjectType,
        info: graphene.ResolveInfo,
        path: str,
    ):
        errors = []
        for field, value in input_object.items():
            field_path = f"{path}.{field}" if path else field
            cleaner_attr = f"clean_{field}"

            if not hasattr(input_object, cleaner_attr):
                continue

            try:
                cleaner_function = getattr(input_object, cleaner_attr)
                cleaned_value = cleaner_function(value, info)
            except ValidationError as e:
                errors.append(ErrorType(field=camel_case(field_path), messages=e.messages))
            else:
                input_object[field] = cleaned_value
                setattr(input_object, field, cleaned_value)
        return errors

    @classmethod
    def clean_nested_inputs(
        cls,
        input_object: InputObjectType,
        info: graphene.ResolveInfo,
        path: str,
    ):
        errors = []
        for field, value in input_object.items():
            field_path = f"{path}.{field}" if path else field

            if isinstance(value, InputObjectType):
                child_errors = cls.clean_input(value, info, path=field_path)
                errors.extend(child_errors)
            elif isinstance(value, list) and value and isinstance(value[0], InputObjectType):
                for index, child_object in enumerate(value):
                    indexed_path = f"{field_path}.{index}"
                    child_errors = cls.clean_input(child_object, info, path=indexed_path)
                    errors.extend(child_errors)
        return errors

    @classmethod
    def check_required_fields(
        cls,
        input_object: InputObjectType,
        info: graphene.ResolveInfo,
        path: str,
    ):
        errors = []

        if not (required_fields := getattr(input_object._meta, "required_fields", None)):
            return []

        for field in required_fields:
            field_path = f"{path}.{field}" if path else field

            if field not in input_object.keys() or input_object[field] is None:
                errors.append(
                    ErrorType(
                        field=camel_case(field_path),
                        messages=["Required field"],
                    )
                )

        return errors

    @classmethod
    def clean_input(
        cls,
        input_object: InputObjectType,
        info: graphene.ResolveInfo,
        path: str,
    ) -> list[ErrorType]:
        errors = []

        required_errors = cls.check_required_fields(input_object, info, path)
        errors.extend(required_errors)

        field_errors = cls.clean_fields(input_object, info, path)
        errors.extend(field_errors)

        if hasattr(input_object, "clean"):
            try:
                input_errors = input_object.clean(info)
            except ValidationError as e:
                errors.append(ErrorType(field=camel_case(path) or "__all__", messages=e.messages))
            else:
                if input_errors:
                    errors.extend(
                        [
                            ErrorType(
                                field=camel_case(f"{path}.{error.field}") if path else error.field,
                                messages=error.messages,
                            )
                            for error in input_errors
                        ]
                    )

        nested_input_errors = cls.clean_nested_inputs(input_object, info, path)
        errors.extend(nested_input_errors)

        return errors

    @classmethod
    def mutate(cls, root, info, **kwargs):  # noqa
        input_object = kwargs[cls._meta.input_name]

        errors = cls.clean_input(input_object, info, path="")
        if errors:
            _set_errors_flag_to_context(info)
            return cls(errors=errors)

        return cls.perform_mutate(info, input_object)

    @classmethod
    def perform_mutate(cls, info: graphene.ResolveInfo, input_object):
        raise NotImplementedError()

    @staticmethod
    def resolve_viewer(root, info, **args):
        if info.context.user.is_authenticated:
            return info.context.user
        return None


class CleanedInputTypeOptions(InputObjectTypeOptions):
    required_fields = None


class CleanedInputType(InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, _meta=None, required_fields=None, **options):
        if not _meta:
            _meta = CleanedInputTypeOptions(cls)
        _meta.required_fields = required_fields
        super().__init_subclass_with_meta__(_meta=_meta, **options)


class TypeModelChoice(ID):
    """
    A GraphQL ID scalar that automatically resolves to a Django model instance.

    Subclass and set `graphql_type` to the GraphQL type:

        class BotID(TypeModelChoice):
            graphql_type = BotType

    When used in a CleanedInputType, the clean_* method receives the resolved
    model instance (not the raw ID string).
    """

    graphql_type = None  # Override in subclass with the GraphQL type

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if isinstance(node, StringValueNode):
            return cls.parse_value(node.value)
        return None

    @classmethod
    def parse_value(cls, value):
        if value is None:
            return None

        try:
            type_name, db_id = from_global_id(value)
        except Exception:
            raise ValidationError(f'Invalid ID format: "{value}"')

        if not type_name:
            raise ValidationError(f'Invalid ID format: "{value}"')

        # Handle multiple allowed types
        if isinstance(cls.graphql_type, (tuple, list)):
            matching_types = [t for t in cls.graphql_type if t._meta.name == type_name]
            if not matching_types:
                allowed = ", ".join(t._meta.name for t in cls.graphql_type)
                raise ValidationError(f'Wrong ID type "{type_name}" for {allowed}.')
            graphql_type = matching_types[0]
        else:
            graphql_type = cls.graphql_type
            if graphql_type._meta.name != type_name:
                raise ValidationError(f'Wrong ID type "{type_name}" passed, expected {graphql_type._meta.name}.')

        # Get the model and query for the instance
        model = graphql_type._meta.model
        try:
            instance = model.objects.get(pk=db_id)
        except model.DoesNotExist:
            raise ValidationError(f'Cannot find {model.__name__} with ID "{value}".')

        return instance


class AccessDenied(GraphQLError):
    pass


# Every access denial — the read floor and explicit write/delete checks alike —
# shares this prefix. It's verb-neutral on purpose: "read" is the floor's
# mechanism, not the user's intent, so someone updating a Bot they can't see is
# told they lack access to it (with an optional "(tried to write)" hint) rather
# than the misleading "you can't read this". Assert against this constant in
# tests so a wording change is one edit, not a suite-wide rewrite.
NO_ACCESS_MESSAGE_PREFIX = "You don't have access to that"

# The login denial is intentionally separate: it's not about a specific object.
NOT_LOGGED_IN_MESSAGE = "You have to be logged in to do this"


def no_access_message(instance, scope=None):
    """User-facing access-denied message for `instance`.

    Pass `scope` (the attempted action) to append a "(tried to …)" debugging
    hint; omit it for the bare read floor.
    """
    base = f"{NO_ACCESS_MESSAGE_PREFIX} {instance._meta.verbose_name}"
    if scope:
        return f"{base} (tried to {scope})"
    return base


def raise_for_access(info, instance, scopes=None):
    if scopes is None:
        scopes = [permissions.SCOPE_WRITE]

    user = info.context.user
    checker = permissions.check.user(user=user, instance=instance)

    for scope in scopes:
        if not checker.can(scope):
            raise AccessDenied(no_access_message(instance, scope))


def parse_deep_errors(e):
    if hasattr(e, "message_dict"):
        messages = []
        for field, field_messages in e.message_dict.items():
            messages.extend(field_messages)
        return messages
    elif hasattr(e, "messages"):
        return e.messages
    return [str(e)]


def join_deep_errors_to_string(e):
    return "; ".join(parse_deep_errors(e))
