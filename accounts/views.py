"""
Accounts Views (FR-01: Authentication, FR-14: Role-Based Authorization)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def profile_view(request):
    """Display user profile and role details."""
    return render(request, "base.html", {
        "page_title": "User Profile",
    })
