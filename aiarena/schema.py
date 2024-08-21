import graphene

from aiarena.graphql.types import Query


schema = graphene.Schema(query=Query)
