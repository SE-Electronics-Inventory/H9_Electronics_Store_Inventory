"""
Inventory Views (FR-03 to FR-09, FR-12, FR-13)
"""
from django.shortcuts import render


def component_list(request):
    """View component inventory list (FR-04, FR-05, FR-08)."""
    return render(request, "base.html", {
        "page_title": "Component Inventory",
    })


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
    return render(request, "base.html", {
        "page_title": "Low-Stock Components",
    })
