from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)


admin.site.register(User, UserAdmin)
