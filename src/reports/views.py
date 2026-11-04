"""
Reports & Dashboard Views (FR-10, FR-11: Generate Inventory Reports)
"""
import csv
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render

from inventory.models import Component


def get_filtered_components(request):
    """
    Helper function to filter active components by category and availability status.
    Used by both report page view and CSV export view.
    """
    components = Component.objects.filter(is_active=True)
    category = request.GET.get("category", "").strip()
    availability = request.GET.get("availability", "").strip()

    # FR-11: Filter by category
    if category:
        components = components.filter(category=category)

    # FR-11: Filter by availability status
    if availability == "In Stock":
        components = components.filter(quantity__gt=F("minimum_stock"))
    elif availability == "Low Stock":
        components = components.filter(quantity__gt=0, quantity__lte=F("minimum_stock"))
    elif availability == "Out of Stock":
        components = components.filter(quantity__lte=0)

    return components.order_by("component_id"), category, availability



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
    """
    Generate and filter inventory reports (FR-11: ESIM-F-011 / TC-REP-01).
    Displays component details, stock quantities, and availability statuses with filtering options.
    """
    if request.GET.get("format") == "csv" or request.GET.get("export") == "csv":
        return export_report_csv(request)

    components, selected_category, selected_availability = get_filtered_components(request)

    # Calculate summary metrics for the report
    total_items = components.count()
    total_units = sum(c.quantity for c in components)
    total_value = sum(c.quantity * c.price for c in components)
    in_stock_count = sum(1 for c in components if c.availability == "In Stock")
    low_stock_count = sum(1 for c in components if c.availability == "Low Stock")
    out_of_stock_count = sum(1 for c in components if c.availability == "Out of Stock")

    context = {
        "page_title": "Inventory Reports",
        "components": components,
        "categories": Component.CATEGORY_CHOICES,
        "selected_category": selected_category,
        "selected_availability": selected_availability,
        "availability_choices": ["In Stock", "Low Stock", "Out of Stock"],
        "total_items": total_items,
        "total_units": total_units,
        "total_value": total_value,
        "in_stock_count": in_stock_count,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "is_filtered": bool(selected_category or selected_availability),
    }
    return render(request, "reports/report_list.html", context)


def export_report_csv(request):
    """
    Export inventory report to downloadable CSV file (FR-11 / Story #56).
    Exports exactly the current filtered data view.
    """
    components, _, _ = get_filtered_components(request)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="inventory_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Component ID",
        "Component Name",
        "Category",
        "Unit Price (INR)",
        "Quantity in Stock",
        "Minimum Stock",
        "Availability Status",
    ])

    for c in components:
        writer.writerow([
            c.component_id,
            c.name,
            c.get_category_display(),
            f"{c.price:.2f}",
            c.quantity,
            c.minimum_stock,
            c.availability,
        ])

    return response
