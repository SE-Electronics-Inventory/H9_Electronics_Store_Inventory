"""
Inventory Views (FR-03 to FR-09, FR-12, FR-13, FR-16, NFR-03)
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import admin_required, has_role, ADMIN
from audit.models import log_change

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
        "can_manage_inventory": is_inventory_administrator(request.user),
    }
    return render(request, "inventory/component_list.html", context)


def is_inventory_administrator(user):
    """Only members of the inventory-administrator group may change inventory (FR-14)."""
    return has_role(user, ADMIN)


@login_required
@admin_required  # FR-14: Staff and Manager get the Access-denied page
def component_add(request):
    """
    Add a new electronic component (FR-03, FR-12, FR-16, NFR-03).
    Runs inside a database transaction (transaction.atomic) so that component creation
    and audit logging complete as one atomic unit or rollback entirely (TC-REL-01).
    """
    form = ComponentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                component = form.save()
                # FR-16: Record inventory addition in audit log
                log_change(
                    component,
                    action="ADD",
                    user=request.user,
                    details=f"Added component {component.component_id} ({component.name}) with initial stock of {component.quantity} units"
                )
        except IntegrityError:
            form.add_error("component_id", "A component with this ID already exists.")
        except Exception:
            messages.error(request, "A database error occurred while saving the component. Transaction was rolled back.")
        else:
            messages.success(request, "Component added successfully.")
            return redirect("inventory:list")
    return render(request, "inventory/component_form.html", {
        "form": form,
        "page_title": "Add Component",
        "submit_label": "Add Component",
    })


@login_required
@admin_required  # FR-14
def component_edit(request, pk):
    """
    Update component details and stock (FR-06, FR-16, NFR-03).
    Runs inside a database transaction (transaction.atomic) ensuring all updates
    and audit logging commit atomically or leave the record unchanged (TC-REL-01).
    """
    component = get_object_or_404(Component, pk=pk)
    form = ComponentForm(request.POST or None, instance=component)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                component = form.save()
                # FR-16: Record inventory update in audit log
                log_change(
                    component,
                    action="EDIT",
                    user=request.user,
                    details=f"Updated component {component.component_id} (stock: {component.quantity}, price: ₹{component.price})"
                )
        except IntegrityError:
            form.add_error("component_id", "A component with this ID already exists.")
        except Exception:
            messages.error(request, "A database error occurred while updating the component. Transaction was rolled back.")
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
    """
    Delete or deactivate component with confirmation (FR-07, FR-16, NFR-03).
    Runs inside a database transaction (transaction.atomic) so that deactivation and
    change log recording succeed or fail atomically without corrupting data (TC-REL-01).
    """
    component = get_object_or_404(Component, pk=pk)
    if request.method == "POST":
        try:
            with transaction.atomic():
                component.is_active = False
                component.save(update_fields=["is_active", "updated_at"])
                # FR-16: Record inventory deactivation in audit log
                log_change(
                    component,
                    action="DELETE",
                    user=request.user,
                    details=f"Deactivated component {component.component_id} ({component.name}) from active inventory"
                )
        except Exception:
            messages.error(request, "A database error occurred while deactivating the component. Transaction was rolled back.")
            return redirect("inventory:list")
        else:
            messages.success(request, "Component deactivated successfully.")
            return redirect("inventory:list")
    return render(request, "inventory/component_confirm_delete.html", {
        "component": component,
    })


def low_stock_list(request):
    """Identify low-stock components (FR-09)."""
    components = Component.objects.filter(
        is_active=True,
        quantity__lte=F("minimum_stock"),
    ).order_by("component_id")
    return render(request, "inventory/low_stock_list.html", {
        "page_title": "Low-Stock Components",
        "components": components,
    })
