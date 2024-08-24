import graphene

from aiarena.graphql.mutations import Mutation
from aiarena.graphql.types import Query


schema = graphene.Schema(query=Query, mutation=Mutation)
