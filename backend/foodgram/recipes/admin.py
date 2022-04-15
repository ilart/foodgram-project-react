from django.contrib import admin

from recipes.models import Tag, Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
