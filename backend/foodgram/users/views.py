from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from recipes.serializer import RecipeSerializerMinified
from recipes.models import Recipe
from users.serializer import SubscribeSerializer, UserSerializer
from users.models import User, Subscribe


SELF_SUBSCRIBE_FORBIDDEN = 'Подписка на самого себя запрещена'
ALREADY_SUBSCRIBED = 'Вы уже подписаны на {} автора'
ERROR_KEY_NAME = 'error'


class SubscribeViewSet(ModelViewSet):
    serializer_class = SubscribeSerializer
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ['following__username', ]
    permission_classes = (IsAuthenticated, )
    queryset = Subscribe.objects.all()


    def destroy(self, request, *args, **kwargs):
        get_object_or_404(
            Subscribe,
            user=request.user.id, subscribing__id=self.kwargs['subscribing']
        ).delete()
        return Response(status=204)
    #

    def create(self, request, *args, **kwargs):
        if self.kwargs['subscribing'] == request.user.id:
            Response({ERROR_KEY_NAME: SELF_SUBSCRIBE_FORBIDDEN}, status=400)
        subscribing = get_object_or_404(User, id=self.kwargs['subscribing'])
        item, created = Subscribe.objects.get_or_create(
            subscribing=subscribing,
            user=request.user
        )
        if not created:
            return Response({ERROR_KEY_NAME: ALREADY_SUBSCRIBED}, status=400)
        recipes = RecipeSerializerMinified(Recipe.objects.filter(author=item.subscribing), many=True).data
        return Response({
            **UserSerializer(subscribing, many=False).data,
            'recipes': recipes,
            'recipes_count': len(recipes)
        }, status=201)
