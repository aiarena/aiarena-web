import graphene
from graphene_django import DjangoObjectType


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
