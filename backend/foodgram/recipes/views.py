from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from recipes.serializer import IngredientSerializer, RecipeSerializer, RecipeSerializerMinified, ShoppingCartSerializer, TagSerializer
from recipes.models import Ingredient, Recipe, ShoppingCart, Tag
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
    pagination_class = LimitOffsetPagination

    @action(detail=True, methods=['delete', 'post'], url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        import pdb
        pdb.set_trace()
        if request.method == 'POST':
            ShoppingCart.objects.create(recipe=get_object_or_404(Recipe, id=pk), user=request.user)
            return Response(RecipeSerializerMinified(id=pk), status=201)
        get_object_or_404(ShoppingCart, user=request.user.id, recipe=self.kwargs.get('pk')).delete()
        return Response(status=204)
    #     return serializer.save(
    #         recipe=get_object_or_404(Recipe, id=self.kwargs.get('recipe_id')),
    #         user=self.request.user
    #     )
    #
    # def destroy(self, request, *args, **kwargs):
    #     get_object_or_404(
    #         ShoppingCart,
    #         user=request.user.id, recipe=kwargs.get('username')
    #     ).delete()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class ShoppingCartViewSet(ModelViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    permission_classes = (IsAuthenticated, )
    url_path = 'recipes'

    def perform_create(self, serializer):
        return serializer.save(
            recipe=get_object_or_404(Recipe, id=self.kwargs.get('recipe_id')),
            user=self.request.user
        )

    def destroy(self, request, *args, **kwargs):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id, recipe=kwargs.get('username')
        ).delete()
