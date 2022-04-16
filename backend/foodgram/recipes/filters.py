import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='contains',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', )
