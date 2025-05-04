from collections import OrderedDict

from django.core.exceptions import ValidationError

import graphene
from graphene import InputObjectType
from graphene.types.inputobjecttype import InputObjectTypeOptions
from graphene.types.mutation import MutationOptions
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import _set_errors_flag_to_context
from graphene_django.types import ErrorType
from graphql import GraphQLError

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
        if hasattr(self, "iterable"):
            return self.iterable.count()
        return len(self)


class DjangoObjectTypeWithUID(DjangoObjectType):
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

    class Meta:
        abstract = True


class CleanedInputMutation(graphene.Mutation):
    class Meta:
        abstract = True

    errors = graphene.List(graphene.NonNull(ErrorType), required=True)

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        _meta=None,
        input_class=None,
        input_name="input",
        arguments=None,
        **options,
    ):
        if not _meta:
            _meta = MutationOptions(cls)

        _meta.input_name = input_name

        assert not arguments, "Can't specify any arguments"
        arguments = OrderedDict({input_name: input_class(required=True)})

        super().__init_subclass_with_meta__(
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

            if field not in input_object.keys() or not input_object[field]:
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


class CleanedInputTypeOptions(InputObjectTypeOptions):
    required_fields = None


class CleanedInputType(InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, _meta=None, required_fields=None, **options):
        if not _meta:
            _meta = CleanedInputTypeOptions(cls)
        _meta.required_fields = required_fields
        super().__init_subclass_with_meta__(_meta=_meta, **options)


def raise_for_access(info, instance, scopes=None):
    if scopes is None:
        scopes = [permissions.SCOPE_WRITE]

    user = info.context.user
    checker = permissions.check.user(user=user, instance=instance)

    for scope in scopes:
        if not checker.can(scope):
            raise GraphQLError(f'{user} cannot perform "{scope}" on "{instance}"')


def parse_deep_errors(e):
    if hasattr(e, "message_dict"):
        messages = []
        for field, field_messages in e.message_dict.items():
            messages.extend(field_messages)
        return messages
    elif hasattr(e, "messages"):
        return e.messages
    return [str(e)]


def raise_graphql_error_from_exception(e):
    raise GraphQLError("; ".join(parse_deep_errors(e)))
