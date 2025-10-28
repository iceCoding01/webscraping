from django.contrib import admin
from .models import JobListing, JobApplication

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'employment_type', 'salary_range', 'is_remote', 'posted_date', 'is_active')
    list_filter = ('employment_type', 'is_remote', 'is_active', 'posted_date')
    search_fields = ('title', 'company', 'description', 'requirements', 'location')
    date_hierarchy = 'posted_date'
    ordering = ('-posted_date',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'status', 'applied_date', 'created_at')
    list_filter = ('status', 'applied_date', 'created_at')
    search_fields = ('user__email', 'user__username', 'job__title', 'job__company', 'notes')
    raw_id_fields = ('user', 'job')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
