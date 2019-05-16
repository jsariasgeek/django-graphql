import graphene
import graphql_jwt
from links.schema import Query as links_query
from links.schema_relay import RelayQuery as links_relay_query
from links.schema_relay import RelayMutation as links_relay_mutation
from links.schema import Mutation as links_mutation
from users.schema import Mutation as users_mutation
from users.schema import Query as users_query

class Query(links_query, links_relay_query, users_query):
    pass 

class Mutation(links_mutation, links_relay_mutation, users_mutation):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)