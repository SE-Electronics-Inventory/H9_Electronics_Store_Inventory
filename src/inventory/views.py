"""
Inventory Views (FR-03 to FR-09, FR-12, FR-13)
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import admin_required, has_role, ADMIN

from .forms import ComponentForm
from .models import Component


def component_list(request):
    """
    View component inventory list with search and filter capabilities (FR-04, FR-05 / TC-SEARCH-01).
    Displays stored component records with details and real-time availability status.
    Supports searching by component ID or name, and filtering by category.
    """
    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    components = Component.objects.filter(is_active=True)

    # FR-05 (#51): Search by ID or name (case-insensitive substring match)
    if query:
        components = components.filter(
            Q(component_id__icontains=query) | Q(name__icontains=query)
        )

    # FR-05 (#52): Filter by category
    if selected_category:
        components = components.filter(category=selected_category)

    components = components.order_by("component_id")

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
        "search_query": query,
        "selected_category": selected_category,
        "categories": Component.CATEGORY_CHOICES,
        "is_filtered": bool(query or selected_category),
    }
    return render(request, "inventory/component_list.html", context)


def is_inventory_administrator(user):
    """Only members of the inventory-administrator group may change inventory (FR-14)."""
    return has_role(user, ADMIN)


@login_required
@admin_required  # FR-14: Staff and Manager get the Access-denied page
def component_add(request):
    """Add a new electronic component (FR-03, FR-12)."""
    form = ComponentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            form.add_error("component_id", "A component with this ID already exists.")
        else:
            messages.success(request, "Component added successfully.")
            return redirect("inventory:list")
    return render(request, "inventory/component_form.html", {
        "form": form,
        "page_title": "Add Component",
        "submit_label": "Add Component",
    })


@admin_required  # FR-14
def component_edit(request, pk):
    """Update component details and stock (FR-06)."""
    component = get_object_or_404(Component, pk=pk)
    form = ComponentForm(request.POST or None, instance=component)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            form.add_error("component_id", "A component with this ID already exists.")
        else:
            messages.success(request, "Component updated successfully.")
            return redirect("inventory:list")
    return render(request, "inventory/component_form.html", {
        "form": form,
        "component": component,
        "page_title": "Edit Component",
        "submit_label": "Save Changes",
    })


@admin_required  # FR-14
def component_delete(request, pk):
    """Delete or deactivate component with confirmation (FR-07)."""
    component = get_object_or_404(Component, pk=pk)
    if request.method == "POST":
        component.is_active = False
        component.save(update_fields=["is_active", "updated_at"])
        messages.success(request, "Component deactivated successfully.")
        return redirect("inventory:list")
    return render(request, "inventory/component_confirm_delete.html", {
        "component": component,
    })


def low_stock_list(request):
    """Identify low-stock components (FR-09)."""
    components = [c for c in Component.objects.filter(is_active=True) if c.is_low_stock]
    return render(request, "inventory/component_list.html", {
        "page_title": "Low-Stock Components",
        "components": components,
        "is_low_stock_filter": True,
    })
