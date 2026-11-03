"""
Audit Admin Configuration
"""
from django.contrib import admin
from .models import ChangeLog


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "component_id", "component_name", "action", "user")
    list_filter = ("action", "timestamp")
    search_fields = ("component_id", "component_name", "user__username")
    readonly_fields = ("component_id", "component_name", "action", "user", "timestamp", "details")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
