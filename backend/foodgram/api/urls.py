from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    SubscribeViewSet,
    IngredientViewSet,
    RecipeViewSet,
    # ShoppingCartViewSet,
    TagsViewSet
)


app_name = 'api'

router_v1 = DefaultRouter()
user_router_v1 = DefaultRouter()

router_v1.register(
    'tags', TagsViewSet, basename='tags'
)
router_v1.register(
    'recipes', RecipeViewSet, basename='recipes'
)
router_v1.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)
router_v1.register(
    'users/subscriptions', SubscribeViewSet, basename='subscriptions'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    # path(
    #     'recipes/<int:recipe>/shopping_cart/',
    #     ShoppingCartViewSet.as_view({
    #         'delete': 'destroy',
    #         'post': 'create'
    #     }), name='shopping_cart'
    # ),
    path(
        'users/<int:subscribing>/subscribe/',
        SubscribeViewSet.as_view({
            'delete': 'destroy',
            'post': 'create'
        }), name='subscribe'
    ),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
