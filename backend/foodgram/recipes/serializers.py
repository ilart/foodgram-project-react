import base64
import uuid

from rest_framework.serializers import BaseSerializer, CharField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.serializers import CurrentUserDefault, HiddenField
# from rest_framework.viewsets import GenericViewSet
# from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientInRecipe, Favorite, Recipe
from recipes.models import ShoppingCart, Tag, TagInRecipe
from recipes.filters import RecipeFilter
from users.serializers import UserSerializer
from foodgram.settings import BASE_URL, BASE_DIR, MEDIA_URL


ENCODING_TYPE = 'UTF-8'
RECIPE_IMAGES = MEDIA_URL + 'recipes/images/'
SPLIT = ';base64,'


def check_user_recipe_in_model(user, recipe, model):
    return True if not user.is_anonymous and model.objects.filter(
        user=user,
        recipe=recipe
    ) else False


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


# class TagInRecipeSerializer(ModelSerializer):
#     name = CharField(source='tag.name', read_only=True)
#     color = CharField(source='tag.color', read_only=True)
#     slug = CharField(source='tag.slug', read_only=True)
#     id = CharField(source='tag.id', read_only=True)
#
#     class Meta:
#         fields = ['id', 'name', 'color', 'slug']
#         model = TagInRecipe


class ImageSerializer(BaseSerializer):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        extension, image = data.split(SPLIT)
        path = f'{RECIPE_IMAGES}{uuid.uuid4().hex}.{extension.split("/")[-1]}'
        with open(BASE_DIR + path, "wb") as handler:
            handler.write(base64.decodebytes(image.encode(ENCODING_TYPE)))
        return BASE_URL + path


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


class RecipeSerializerMinified(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


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
