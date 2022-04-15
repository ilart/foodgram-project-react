import base64
import uuid

from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag, TagInRecipe
from recipes.filters import RecipeFilter
from users.serializer import UserSerializer
from foodgram.settings import BASE_URL, MEDIA_ROOT, MEDIA_URL


RECIPE_IMAGES = 'recipes/images/'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        fields = ['name', 'measurement_unit', 'amount']
        model = IngredientInRecipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='tag.name', read_only=True)
    color = serializers.CharField(source='tag.color', read_only=True)
    slug = serializers.CharField(source='tag.slug', read_only=True)
    id = serializers.CharField(source='tag.id', read_only=True)

    class Meta:
        fields = ['id', 'name', 'color', 'slug']
        model = TagInRecipe


class ImageSerializer(serializers.BaseSerializer):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        format, image = data.split(';base64,')
        image_encode = image.encode('UTF-8')
        filename = uuid.uuid4().hex + '.' + format.split('/')[-1]
        with open(
                MEDIA_ROOT+'/'+RECIPE_IMAGES+filename,
                "wb"
        ) as handler:
            handler.write(base64.decodebytes(image_encode))
        return BASE_URL + MEDIA_URL + RECIPE_IMAGES + filename



class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    # tags = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = ImageSerializer()

    class Meta:
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time']
        model = Recipe
        filter_class = RecipeFilter

    def get_ingredients(self, item):
        return IngredientInRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=item.id), many=True
        ).data

    # def get_tags(self, item):
    #     import pdb
    #     pdb.set_trace()
    #     return TagSerializer(item.tags, many=True).data

    def create(self, validated_data):
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=self.context.get('request').user)
        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            TagInRecipe.objects.create(recipe=recipe, tag=current_tag)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientInRecipe.objects.create(recipe=recipe, ingredient=current_ingredient, amount=ingredient['amount'])
        return recipe


class RecipeSerializerMinified(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
