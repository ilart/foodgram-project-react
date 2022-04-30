from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import RecipePaginator
from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    RecipeSerializerMinified,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer
)
from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import User, Subscribe


SELF_SUBSCRIBE_FORBIDDEN = 'Подписка на самого себя запрещена'
ALREADY_SUBSCRIBED = 'Вы уже подписаны на {user} автора'
ERROR = 'error'
FILE_FORMAT = '| {name: <30}| {amount: >10} {unit: <10}\n'
CONTENT_TYPE = 'text/plain'
CART_FILENAME = 'cart.txt'
HEADER = ('| Наименование                  | Количество \n' +
          '|-------------------------------|--------------\n')


class TagsViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    lookup_field = 'id'
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = RecipePaginator
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(RecipeListSerializer(
            self.perform_create(serializer),
            context={'request': request}
        ).data)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(RecipeListSerializer(
            self.perform_update(serializer),
            context={'request': request}
        ).data)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        cart = (
            IngredientInRecipe.objects
            .filter(recipe__in=(ShoppingCart.objects
                    .filter(user=request.user.id)
                    .values('recipe')))
            .values('ingredient_id__name', 'ingredient_id__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename="{CART_FILENAME}"'
        )
        lines = [HEADER]
        for item in cart:
            lines.append(FILE_FORMAT.format(
                name=item['ingredient_id__name'],
                amount=item['total_amount'],
                unit=item['ingredient_id__measurement_unit'])
            )
        response.writelines(lines)
        return response

    def add_remove_recipe_model(self, method, user, model, pk):
        if method == 'POST':
            recipe = self.get_object()
            item, created = model.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if not created:
                return Response(status=400)
            return Response(
                RecipeSerializerMinified(recipe, many=False).data,
                status=201
            )
        get_object_or_404(
            model,
            user=user.id,
            recipe=pk).delete()
        return Response(status=204)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        return self.add_remove_recipe_model(
            request.method, request.user, Favorite, pk
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return self.add_remove_recipe_model(
            request.method, request.user, ShoppingCart, pk
        )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeCreateSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    permission_classes = (permissions.IsAuthenticated,)


class SubscribeViewSet(ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def destroy(self, request, subscribing):
        get_object_or_404(
            Subscribe,
            user=request.user.id, subscribing__id=subscribing
        ).delete()
        return Response(status=204)

    def create(self, request, subscribing):
        if subscribing == request.user.id:
            return Response({ERROR: SELF_SUBSCRIBE_FORBIDDEN}, status=400)
        subscribing_user = get_object_or_404(User, id=subscribing)
        item, created = Subscribe.objects.get_or_create(
            subscribing=subscribing_user,
            user=request.user
        )
        if not created:
            return Response(
                {ERROR: ALREADY_SUBSCRIBED.format(
                    user=subscribing_user.username
                )},
                status=400
            )
        return Response(SubscribeSerializer(
            item,
            many=False,
            context={'request': request}).data, status=201)

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)
