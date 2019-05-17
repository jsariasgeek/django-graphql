import graphene
from graphene_django import DjangoObjectType
from users.schema import UserType
from graphql import GraphQLError
from .models import Link, Vote
from django.db.models import Q

class LinkType(DjangoObjectType):
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        print('Token')
        print(info.context.user)
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('Not Logged In')

        print(user.is_anonymous)
        print(user)
        link = Link(
            url=url, 
            description=description, 
            posted_by=user)
        
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )

class CreateVote(graphene.Mutation):
    id = graphene.Int()
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise GraphQLError('Invalid Link')
        
        vote = Vote(
            user=user,
            link=link,
        )

        vote.save()

        return CreateVote(user=user, link=link, id=vote.id)

class DeleteLink(graphene.Mutation):
    deleted = graphene.Boolean()

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        link_to_delete = Link.objects.get(pk=link_id)
        link_to_delete.delete()
        return DeleteLink(deleted=True)

class Query(graphene.ObjectType):
    links = graphene.List(
        LinkType, 
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        )
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)
        
        if skip:
            qs = qs[skip:]
        
        if first:
            qs = qs[:first]

        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    delete_link = DeleteLink.Field()
    create_vote = CreateVote.Field()
