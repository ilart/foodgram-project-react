import base64
import uuid

from rest_framework.serializers import BaseSerializer, CharField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.serializers import CurrentUserDefault, HiddenField
from rest_framework.validators import UniqueTogetherValidator

from api.filters import RecipeFilter
from recipes.models import Ingredient, IngredientInRecipe, Favorite, Recipe
from recipes.models import ShoppingCart, Tag, TagInRecipe
from foodgram.settings import BASE_DIR, MEDIA_URL
from users.models import Subscribe, User


ENCODING_TYPE = 'UTF-8'
RECIPE_IMAGES = MEDIA_URL + 'recipes/images/'
SPLIT = ';base64,'


def check_user_recipe_in_model(user, recipe, model):
    return True if not user.is_anonymous and model.objects.filter(
        user=user,
        recipe=recipe
    ) else False


SELF_FOLLOW_FORBIDDEN = 'Подписка на самогосебя запрещена.'


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

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


class RecipeSerializerMinified(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscribeSerializer(ModelSerializer):
    email = CharField(
        source='subscribing.email',
        read_only=True
    )
    id = CharField(
        source='subscribing.id',
        read_only=True
    )
    username = CharField(
        source='subscribing.username',
        read_only=True
    )
    first_name = CharField(
        source='subscribing.first_name',
        read_only=True
    )
    last_name = CharField(
        source='subscribing.last_name',
        read_only=True
    )
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

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


class IngredientSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientInRecipeSerializer(ModelSerializer):
    id = CharField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = IngredientInRecipe
        read_only = ['id', 'name', 'measurement_unit']


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ImageSerializer(BaseSerializer):
    def to_representation(self, value):
        return self.context['request'].build_absolute_uri('value')

    def to_internal_value(self, data):
        extension, image = data.split(SPLIT)
        path = f'{RECIPE_IMAGES}{uuid.uuid4().hex}.{extension.split("/")[-1]}'
        with open(BASE_DIR + path, "wb") as handler:
            handler.write(base64.decodebytes(image.encode(ENCODING_TYPE)))
        return path


class RecipeSerializer(ModelSerializer):
    ingredients = SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = ImageSerializer()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart'
        ]
        model = Recipe
        filter_class = RecipeFilter

    def get_is_favorited(self, item):
        return check_user_recipe_in_model(
            self.context['request'].user,
            item,
            Favorite
        )

    def get_is_in_shopping_cart(self, item):
        return check_user_recipe_in_model(
            self.context['request'].user,
            item,
            ShoppingCart
        )

    def get_ingredients(self, item):
        return IngredientInRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=item.id), many=True
        ).data

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        for tag in self.initial_data.pop('tags'):
            TagInRecipe.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(id=tag)
            )
        for ingredient in self.initial_data.pop('ingredients'):
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.tags.clear()
        instance.ingredients.clear()
        for tag in self.initial_data.pop('tags'):
            TagInRecipe.objects.create(
                recipe=instance,
                tag=Tag.objects.get(id=tag)
            )
        for ingredient in self.initial_data.pop('ingredients'):
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        instance.save()
        return instance


class ShoppingCartSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    recipe = RecipeSerializerMinified(read_only=True, default='')

    class Meta:
        model = ShoppingCart
        fields = ['recipe', 'user']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['recipe', 'user']
            )
        ]
