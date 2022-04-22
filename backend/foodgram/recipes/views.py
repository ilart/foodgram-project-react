from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import Ingredient, IngredientInRecipe, Favorite, Recipe, ShoppingCart, Tag
from recipes.serializer import IngredientSerializer, RecipeSerializer, RecipeSerializerMinified, ShoppingCartSerializer, TagSerializer


FILE_FORMAT = '{name}: {amount} {unit}\n'
CART_FILENAME = 'cart.txt'

class TagsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    lookup_field = 'id'


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('tags',)
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination


    def get_queryset(self):
        queryset = Recipe.objects.all()
        for name, model in {'is_in_shopping_cart': ShoppingCart, 'is_favorited': Favorite}.items():
            value = self.request.query_params.get(name)
            if value and int(value) == 1:
                queryset = queryset.filter(id__in=model.objects.filter(user=self.request.user).values('recipe'))
        return queryset



    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        if request.user.is_anonymous:
            return Response(status=HTTP_403_FORBIDDEN)
        cart = (
            IngredientInRecipe.objects
            .filter(recipe__in=(ShoppingCart.objects
                    .filter(user=request.user.id)
                    .values('recipe')))
            .values('ingredient_id__name', 'ingredient_id__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(CART_FILENAME)
        lines = []
        for item in cart:
            lines.append(FILE_FORMAT.format(
                name=item['ingredient_id__name'],
                amount=item['amount'],
                unit=item['ingredient_id__measurement_unit'])
            )
        response.writelines(lines)
        return response


    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        if request.method == 'POST':
            recipe = self.get_object()
            item, created = Favorite.objects.get_or_create(recipe=recipe, user=request.user)
            if not created:
                return Response(status=400)
            return Response(RecipeSerializerMinified(recipe, many=False).data, status=201)
        get_object_or_404(Favorite, user=request.user.id, recipe=self.kwargs.get('pk')).delete()
        return Response(status=204)


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class ShoppingCartViewSet(ModelViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        if ShoppingCart.objects.filter(recipe=self.kwargs.get('recipe'), user=self.request.user):
            return Response(status=400)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe'))
        serializer = self.get_serializer(
            data={'recipe': recipe, 'user': self.request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data['recipe'], status=201, headers=headers)

    def destroy(self, request, *args, **kwargs):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id, recipe=self.kwargs.get('recipe')
        ).delete()
        return Response(status=204)
