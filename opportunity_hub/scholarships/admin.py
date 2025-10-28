from django.contrib import admin
from .models import Scholarship, ScholarshipApplication

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'education_level', 'country', 'deadline', 'is_fully_funded', 'is_active')
    list_filter = ('education_level', 'country', 'is_fully_funded', 'is_active')
    search_fields = ('title', 'organization', 'description', 'requirements')
    date_hierarchy = 'deadline'
    ordering = ('-created_at',)

@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'scholarship', 'status', 'applied_date', 'created_at')
    list_filter = ('status', 'applied_date', 'created_at')
    search_fields = ('user__email', 'user__username', 'scholarship__title', 'notes')
    raw_id_fields = ('user', 'scholarship')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
