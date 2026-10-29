"""
Reports & Dashboard Views (FR-10, FR-11)
"""
from django.shortcuts import render


def dashboard(request):
    """Inventory overview dashboard (FR-10)."""
    return render(request, "base.html", {
        "page_title": "Inventory Dashboard",
    })


def report_list(request):
    """Generate and filter inventory reports (FR-11)."""
    return render(request, "base.html", {
        "page_title": "Inventory Reports",
    })
