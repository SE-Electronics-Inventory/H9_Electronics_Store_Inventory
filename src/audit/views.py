"""
Audit Log Views (FR-16: Implement Inventory Change Tracking)
"""
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from accounts.roles import admin_required
from .models import ChangeLog


@login_required
@admin_required  # FR-14 / FR-16: change history is for the Inventory Administrator only
def log_list(request):
    """
    Inventory change tracking history log (FR-16: Story #58 / TC-AUD-01).
    Displays a chronological history (newest first) of all add, edit, and delete operations.
    """
    logs = ChangeLog.objects.all().select_related("user")

    action_filter = request.GET.get("action", "").strip()
    query = request.GET.get("q", "").strip()

    if action_filter:
        logs = logs.filter(action=action_filter)

    if query:
        logs = logs.filter(
            Q(component_id__icontains=query) | Q(component_name__icontains=query)
        )

    logs = logs.order_by("-timestamp")

    context = {
        "page_title": "Inventory Change Tracking (Audit Trail)",
        "logs": logs,
        "total_logs": logs.count(),
        "selected_action": action_filter,
        "search_query": query,
        "action_choices": ChangeLog.ACTION_CHOICES,
        "is_filtered": bool(action_filter or query),
    }
    return render(request, "audit/log_list.html", context)
