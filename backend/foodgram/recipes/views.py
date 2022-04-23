from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework import viewsets

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import Ingredient, IngredientInRecipe, Favorite, Recipe
from recipes.models import ShoppingCart, Tag
from recipes.serializers import IngredientSerializer, RecipeSerializerMinified
from recipes.serializers import RecipeSerializer, ShoppingCartSerializer
from recipes.serializers import TagSerializer


FILE_FORMAT = '| {name: <30}| {amount: >10} {unit: <10}\n'
CONTENT_TYPE = 'text/plain'
CART_FILENAME = 'cart.txt'
HEADER = ('| Наименование                  | Количество \n' +
          '|-------------------------------|--------------\n')


class TagsViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    lookup_field = 'id'


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('tags',)
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Recipe.objects.all()
        for name, model in {
            'is_in_shopping_cart': ShoppingCart,
            'is_favorited': Favorite
        }.items():
            value = self.request.query_params.get(name)
            if value and int(value) == 1:
                queryset = queryset.filter(id__in=model.objects.filter(
                    user=self.request.user
                ).values('recipe'))
        return queryset

    @action(detail=False, methods=['get'])
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
        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename="{CART_FILENAME}"'
        )
        lines = [HEADER]
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
            item, created = Favorite.objects.get_or_create(
                recipe=recipe,
                user=request.user
            )
            if not created:
                return Response(status=400)
            return Response(
                RecipeSerializerMinified(recipe, many=False).data,
                status=201
            )
        get_object_or_404(
            Favorite,
            user=request.user.id,
            recipe=pk).delete()
        return Response(status=204)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, recipe):
        if ShoppingCart.objects.filter(
                recipe=recipe,
                user=self.request.user
        ):
            return Response(status=400)
        recipe = get_object_or_404(Recipe, id=recipe)
        serializer = self.get_serializer(
            data={'recipe': recipe, 'user': self.request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data['recipe'], status=201, headers=headers)

    def destroy(self, request, recipe):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id, recipe=recipe
        ).delete()
        return Response(status=204)
