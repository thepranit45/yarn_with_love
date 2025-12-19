from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_artisan', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_artisan', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'is_artisan', 'bio')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
