import base64
import uuid

from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientInRecipe, Favorite, Recipe, ShoppingCart, Tag, TagInRecipe
from recipes.filters import RecipeFilter
from users.serializer import UserSerializer
from foodgram.settings import BASE_URL, BASE_DIR, MEDIA_URL


RECIPE_IMAGES = MEDIA_URL + 'recipes/images/'

def check_recipe_in_model(user, recipe, model):
    return True if model.objects.filter(
            user=user,
            recipe=recipe
        ) else False

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = IngredientInRecipe
        read_only = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


# class TagInRecipeSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='tag.name', read_only=True)
#     color = serializers.CharField(source='tag.color', read_only=True)
#     slug = serializers.CharField(source='tag.slug', read_only=True)
#     id = serializers.CharField(source='tag.id', read_only=True)
#
#     class Meta:
#         fields = ['id', 'name', 'color', 'slug']
#         model = TagInRecipe


class ImageSerializer(serializers.BaseSerializer):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        format, image = data.split(';base64,')
        path = RECIPE_IMAGES + uuid.uuid4().hex + '.' + format.split('/')[-1]
        with open(BASE_DIR+path, "wb") as handler:
            handler.write(base64.decodebytes(image.encode('UTF-8')))
        return BASE_URL + path


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = ImageSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart']
        model = Recipe
        filter_class = RecipeFilter

    def get_is_favorited(self, item):
        return check_recipe_in_model(self.context['request'].user, item, Favorite)

    def get_is_in_shopping_cart(self, item):
        return check_recipe_in_model(self.context['request'].user, item, ShoppingCart)


    def get_ingredients(self, item):
        return IngredientInRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=item.id), many=True
        ).data

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data, author=self.context.get('request').user)
        for tag in self.initial_data.pop('tags'):
            TagInRecipe.objects.create(recipe=recipe, tag=Tag.objects.get(id=tag))
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
            TagInRecipe.objects.create(recipe=instance, tag=Tag.objects.get(id=tag))
        for ingredient in self.initial_data.pop('ingredients'):
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        instance.save()
        return instance


class RecipeSerializerMinified(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
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
