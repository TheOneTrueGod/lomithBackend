"""
Admin configuration for the auth app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AIIntegration


@admin.register(AIIntegration)
class AIIntegrationAdmin(admin.ModelAdmin):
    """
    Admin interface for AI Integration model.
    """
    list_display = ['user', 'provider', 'model', 'name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'provider', 'name', 'model']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Provider Configuration', {
            'fields': ('provider', 'model', 'base_url', 'name')
        }),
        ('API Key', {
            'fields': ('encrypted_api_key',),
            'description': 'API key is stored encrypted. Use the API endpoints to set/update keys securely.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

