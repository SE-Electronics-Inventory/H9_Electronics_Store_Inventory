"""
Reports & Dashboard Views (FR-10, FR-11)
"""
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import render

from accounts.roles import ADMIN, MANAGER, role_required
from inventory.models import Component


@login_required
@role_required(ADMIN, MANAGER)
def dashboard(request):
    """Show live inventory totals and components at or below their stock threshold."""
    active_components = Component.objects.filter(is_active=True)
    low_stock_components = active_components.filter(quantity__lte=F("minimum_stock"))
    available_stock = active_components.aggregate(total=Sum("quantity"))["total"] or 0
    return render(request, "reports/dashboard.html", {
        "page_title": "Inventory Dashboard",
        "total_components": active_components.count(),
        "available_stock": available_stock,
        "low_stock_count": low_stock_components.count(),
        "low_stock_components": low_stock_components.order_by("component_id"),
    })


def report_list(request):
    """Generate and filter inventory reports (FR-11)."""
    return render(request, "base.html", {
        "page_title": "Inventory Reports",
    })
