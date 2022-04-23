from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscribe, User


SELF_FOLLOW_FORBIDDEN = 'Подписка на самогосебя запрещена.'


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, item):
        user = self.context['request'].user
        return (user.subscribed.filter(subscribing__id=item.id)
                .exists()) if not user.is_anonymous else False


class RecipeSerializerMinified(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        source='subscribing.email',
        read_only=True
    )
    id = serializers.CharField(
        source='subscribing.id',
        read_only=True
    )
    username = serializers.CharField(
        source='subscribing.username',
        read_only=True
    )
    first_name = serializers.CharField(
        source='subscribing.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        source='subscribing.last_name',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscribe
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']

    def get_recipes(self, item):
        return RecipeSerializerMinified(
            item.subscribing.recipes, many=True
        ).data

    def get_recipes_count(self, item):
        return item.subscribing.recipes.all().count()

    def get_is_subscribed(self, item):
        user = self.context['request'].user
        return (user.subscribed.filter(subscribing__id=item.subscribing.id)
                .exists()) if not user.is_anonymous else False
