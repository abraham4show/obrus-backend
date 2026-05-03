from django.contrib import admin
from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'full_name', 'company_name', 'service_type', 
        'status', 'created_at', 'user'
    ]
    list_filter = ['service_type', 'status', 'created_at']
    search_fields = ['full_name', 'company_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Client Information', {
            'fields': ('full_name', 'company_name', 'phone', 'email', 'location')
        }),
        ('Service Details', {
            'fields': ('service_type', 'service_details')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'user', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
