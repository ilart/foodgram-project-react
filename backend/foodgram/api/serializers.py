import base64
import uuid

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


NO_FIELD = 'Поле {name} не обнаружено.'
INTEGER_POSITIVE = 'Поле {name} должно быть целым положительным числом.'
DUPLICATE = 'Обнаржуено дублирование ингредиента id:"{id}"'
ENCODING_TYPE = 'UTF-8'
RECIPE_IMAGES = MEDIA_URL + 'recipes/images/'
SPLIT = ';base64,'
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
        fields = ['id',]


class TagListSerializer(ModelSerializer):
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
    id = IntegerField(required=True)
    class Meta:
        model = Ingredient
        fields = ['id',]

class RecipeSerializer(ModelSerializer):
    # ingredients = IngredientCreateSerializer(many=True)
    ingredients = SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = ImageSerializer()

    class Meta:
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time'
        ]
        model = Recipe
        filter_class = RecipeFilter

    def validate(self, data):
        import pdb
        pdb.set_trace()
        ingredients = set()
        for ingredient in self.initial_data['ingredients']:
            id = ingredient.get('id')
            if not id:
                raise ValidationError(NO_FIELD.format(name='id'))
            if type(id) != int or id < 1:
                raise ValidationError(INTEGER_POSITIVE.format(name='id'))
            if id in ingredients:
                raise ValidationError(DUPLICATE.format(id=id))
            ingredients.add(id)
            amount = ingredient.get('amount')
            if not amount:
                raise ValidationError(NO_FIELD.format(name='amount'))
            if type(amount) != int or amount < 1:
                raise ValidationError(INTEGER_POSITIVE.format(name='amount'))
        data['ingredients'] = self.initial_data['ingredients']
        cooking_time = data['cooking_time']
        if not cooking_time:
            raise ValidationError(NO_FIELD.format(name='cooking_time'))
        if type(cooking_time) != int or cooking_time < 1:
            raise ValidationError(INTEGER_POSITIVE.format(name='cooking_time'))
        return data

    def get_ingredients(self, item):
        return IngredientInRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=item.id), many=True
        ).data

    def create(self, validated_data):
        import pdb
        pdb.set_trace()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )

        for tag in tags:
            TagInRecipe.objects.create(
                recipe=recipe,
                tag=get_object_or_404(Tag, id=tag.id)
            )
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.tags.clear()
        instance.ingredients.clear()
        for tag in validated_data.pop('tags'):
            TagInRecipe.objects.create(
                recipe=instance,
                tag=get_object_or_404(Tag, id=tag.id)
            )
        for ingredient in validated_data.pop('ingredients'):
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            )
        instance.save()
        return instance


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
