from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from recipes.serializer import IngredientSerializer, RecipeSerializer, TagSerializer
from recipes.models import Ingredient, Recipe, Tag
from recipes.filters import RecipeFilter


class TagsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    lookup_field = 'id'


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('tags',)
    filter_class = RecipeFilter

    # def get_serializer_class(self):
    #     if self.action in ['list', 'retrieve']:
    #         return RecipeSerializer
    #     return RecipeCreateSerializer
    # def perform_create(self, serializer):
    #     serializer.save(
    #         author=self.request.user
    #     )

    # def create(self, request):
    #     import pdb
    #     pdb.set_trace()

class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
