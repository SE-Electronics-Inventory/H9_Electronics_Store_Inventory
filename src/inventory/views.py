"""
Inventory Views (FR-03 to FR-09, FR-12, FR-13)
"""
from django.shortcuts import render, get_object_or_404
from .models import Component


def component_list(request):
    """
    View component inventory list (ESIM-F-004 / TC-INV-02).
    Displays stored component records with details and real-time availability status.
    """
    components = Component.objects.filter(is_active=True).order_by("component_id")

    # Metrics for quick inventory status overview
    total_components = components.count()
    in_stock_count = sum(1 for c in components if c.availability == "In Stock")
    low_stock_count = sum(1 for c in components if c.availability == "Low Stock")
    out_of_stock_count = sum(1 for c in components if c.availability == "Out of Stock")

    context = {
        "page_title": "Component Inventory",
        "components": components,
        "total_components": total_components,
        "in_stock_count": in_stock_count,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }
    return render(request, "inventory/component_list.html", context)


def component_add(request):
    """Add a new electronic component (FR-03, FR-12)."""
    return render(request, "base.html", {
        "page_title": "Add Component",
    })


def component_edit(request, pk):
    """Update component details and stock (FR-06)."""
    return render(request, "base.html", {
        "page_title": "Edit Component",
    })


def component_delete(request, pk):
    """Delete or deactivate component with confirmation (FR-07)."""
    return render(request, "base.html", {
        "page_title": "Delete Component",
    })


def low_stock_list(request):
    """Identify low-stock components (FR-09)."""
    components = [c for c in Component.objects.filter(is_active=True) if c.is_low_stock]
    return render(request, "inventory/component_list.html", {
        "page_title": "Low-Stock Components",
        "components": components,
        "is_low_stock_filter": True,
    })
