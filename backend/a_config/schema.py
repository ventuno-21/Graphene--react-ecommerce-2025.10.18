import graphene
import graphql_jwt
from graphene_django.debug import DjangoDebug

from account.schema import AccountMutation, AccountQuery
from shop.schema import ShopMutation, ShopQuery


class Query(ShopQuery, AccountQuery, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug)


# class Query(account.schema.Query, shop.schema.Query, graphene.ObjectType):
#     debug = graphene.Field(DjangoDebug)


class Mutation(AccountMutation, ShopMutation, graphene.ObjectType):
    # JWT Mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
