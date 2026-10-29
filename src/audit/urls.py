"""
Audit URL Configuration (FR-16)
"""
from django.urls import path
from . import views

app_name = "audit"

urlpatterns = [
    path("", views.log_list, name="log_list"),
]
