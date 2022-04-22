# from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import SubscribeViewSet
from recipes.views import IngredientViewSet, RecipeViewSet, ShoppingCartViewSet, TagsViewSet

app_name = 'api'


router_v1 = DefaultRouter()
user_router_v1 = DefaultRouter()

# urlpatterns = [
#     path('users/me/', get_me, name='user_me'),
#     path('auth/signup/', validate_token, name='validation'),
#     path('auth/token/', get_token, name='request_token'),
#     path('', include(router_v1.urls)),
# ]
#
# user_router_v1.register(
#     'users', UsersViewSet, basename='users'
# )
router_v1.register(
    'tags', TagsViewSet, basename='tags'
)

router_v1.register(
    'recipes', RecipeViewSet, basename='recipes'
)

router_v1.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)

# router_v1.register(
#     r'users/(?P<subscribing>\d+)/subscribe',
#     SubscribeViewSet,
#     basename='subscriptions'
# )

# router_v1.register(
#     'users/subscriptions', SubscribeViewSet, basename='subscriptions'
# )

# router_v1.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     ShoppingCartViewSet,
#     basename='shopping_cart'
# )

urlpatterns = [
    # path('', include(user_router_v1.urls)),
    # path('users/me/', get_me, name='user_me'),
    path('', include(router_v1.urls)),
    path('recipes/<int:recipe>/shopping_cart/', ShoppingCartViewSet.as_view({
        'delete': 'destroy',
        'post': 'create'
        }), name='shopping_cart'),
    path('users/<int:subscribing>/subscribe/', SubscribeViewSet.as_view({
        'delete': 'destroy',
        'post': 'create'
        }), name='subscribe'),
    # path(r'users/(?P<following>\d+)/subscribe', ShoppingCartViewSet, name='shopping_cart'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
