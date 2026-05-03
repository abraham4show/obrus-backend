from django.contrib import admin
from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'full_name', 'position', 'status', 
        'created_at', 'user'
    ]
    list_filter = ['status', 'position', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'position']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('Application Details', {
            'fields': ('position', 'cv', 'photo')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'user', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
