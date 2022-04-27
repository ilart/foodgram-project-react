from django.shortcuts import get_object_or_404
from rest_framework.response import Response


def check_user_recipe_in_model(user, recipe, model):
    return True if not user.is_anonymous and model.objects.filter(
        user=user,
        recipe=recipe
    ) else False
