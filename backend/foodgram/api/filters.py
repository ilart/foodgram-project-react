import django_filters

from recipes.models import Ingredient, Recipe


def filter_user_recipes_in_model(queryset, user, model, value):
    if value:
        return queryset.filter(**{model + '__user': user})
    return queryset


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        widget=django_filters.widgets.BooleanWidget
    )

    is_favorited = django_filters.BooleanFilter(
        method='get_is_favorited',
        widget=django_filters.widgets.BooleanWidget
    )

    def get_is_in_shopping_cart(self, queryset, name, value):
        return filter_user_recipes_in_model(
            queryset, self.request.user, 'shoppingcart', value
        )

    def get_is_favorited(self, queryset, name, value):
        return filter_user_recipes_in_model(
            queryset, self.request.user, 'favorite', value
        )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited']


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name', ]
