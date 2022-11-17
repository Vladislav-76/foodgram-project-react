from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (Subscriptions)

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name')
    list_filter = ('email', 'username')


admin.site.register([Subscriptions, ])
