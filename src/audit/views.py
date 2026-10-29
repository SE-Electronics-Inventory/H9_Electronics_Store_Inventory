"""
Audit Log Views (FR-16)
"""
from django.shortcuts import render

from accounts.roles import admin_required


@admin_required  # FR-14: change history is for the Inventory Administrator only
def log_list(request):
    """Inventory change tracking history log (FR-16)."""
    return render(request, "base.html", {
        "page_title": "Audit Trail & Change History",
    })
