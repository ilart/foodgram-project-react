import base64
import uuid

from django.core.paginator import Paginator
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    BaseSerializer,
    CharField,
    CurrentUserDefault,
    HiddenField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ValidationError
)
from rest_framework.validators import UniqueTogetherValidator

from api.filters import RecipeFilter
from api.utils import check_user_recipe_in_model
from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag,
    TagInRecipe
)
from foodgram.settings import BASE_DIR, BASE_URL, MEDIA_URL
from users.models import Subscribe, User


COOKING_TIME_ERROR = 'Время приготовления не может быть меньше 1 минуты'
DUPLICATE = 'Обнаржуено дублирование ингредиента id:"{id}"'
ENCODING_TYPE = 'UTF-8'
RECIPE_IMAGES = MEDIA_URL + 'recipes/images/'
SPLIT = ';base64,'


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

    # def get_recipes(self, item):

    def get_recipes(self, item):
        return RecipeSerializerMinified(
            Paginator(
                item.subscribing.recipes.all(),
                (
                    self.context['request'].query_params.get('recipes_limit'))
            ).page(
                self.context['request'].query_params.get('page')
            ), many=True
        ).data

        # return RecipeSerializerMinified(
        #     item.subscribing.recipes, many=True
        # ).data

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
        return f'{BASE_URL}{value}'

    def to_internal_value(self, data):
        extension, image = data.split(SPLIT)
        path = f'{RECIPE_IMAGES}{uuid.uuid4().hex}.{extension.split("/")[-1]}'
        with open(BASE_DIR + path, "wb") as handler:
            handler.write(base64.decodebytes(image.encode(ENCODING_TYPE)))
        return path


class IngredientCreateSerializer(ModelSerializer):
    id = IntegerField(required=True, source='ingredient')
    amount = IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount']


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    author = UserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = ImageSerializer()
    cooking_time = IntegerField(
        validators=[MinValueValidator(1, COOKING_TIME_ERROR)]
    )

    class Meta:
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time'
        ]
        model = Recipe
        filter_class = RecipeFilter

    def validate(self, data):
        ingredients = set()
        for ingredient in data['ingredients']:
            if ingredient['ingredient'] in ingredients:
                raise ValidationError(
                    DUPLICATE.format(id=ingredient['ingredient'])
                )
            ingredients.add(ingredient['ingredient'])
        return data

    def add_tags_ingredients_to_recipe(self, recipe, tags, ingredients):
        for tag in tags:
            TagInRecipe.objects.create(
                recipe=recipe,
                tag=get_object_or_404(Tag, id=tag.id)
            )
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient['ingredient']
                ),
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        self.add_tags_ingredients_to_recipe(recipe, tags, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.ingredients.clear()
        self.add_tags_ingredients_to_recipe(
            recipe,
            validated_data.pop('tags'),
            validated_data.pop('ingredients')
        )
        recipe.save()
        return super().update(recipe, validated_data)


class RecipeListSerializer(ModelSerializer):
    ingredients = SerializerMethodField()
    author = UserSerializer()
    tags = TagSerializer(many=True)
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
