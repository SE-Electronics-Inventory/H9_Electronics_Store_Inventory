"""Friendly error handlers for production requests."""

from django.shortcuts import render


def page_not_found(request, exception):
    """Render a safe, user-facing page for missing routes and records."""
    return render(request, "404.html", status=404)


def server_error(request):
    """Render a generic server error without exposing exception details."""
    return render(request, "500.html", status=500)
