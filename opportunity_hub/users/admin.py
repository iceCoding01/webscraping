from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)