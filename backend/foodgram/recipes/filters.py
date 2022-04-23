import django_filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='contains',
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name', ]
