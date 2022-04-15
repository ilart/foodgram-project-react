# from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import FollowViewSet
from recipes.views import IngredientViewSet, RecipeViewSet, TagsViewSet

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
router_v1.register(
    r'users/(?P<following>\d+)/subscribe', FollowViewSet, basename='subscriptions'
)

router_v1.register(
    'users/subscriptions', FollowViewSet, basename='subscriptions'
)

urlpatterns = [
    # path('', include(user_router_v1.urls)),
    # path('users/me/', get_me, name='user_me'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
