"""
Accounts Views (FR-01: Authentication, FR-14: Role-Based Authorization)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


@login_required
@never_cache
def profile_view(request):
    """Display user profile and role details without caching private data."""
    return render(request, "base.html", {
        "page_title": "User Profile",
    })
