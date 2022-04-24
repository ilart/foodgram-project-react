from django.contrib import admin

from users.models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
