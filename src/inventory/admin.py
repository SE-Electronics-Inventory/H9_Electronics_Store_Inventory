"""
Inventory Django Admin Configuration
"""
from django.contrib import admin
from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = (
        "component_id",
        "name",
        "category",
        "price",
        "quantity",
        "minimum_stock",
        "availability",
        "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("component_id", "name", "description")
    ordering = ("component_id",)
